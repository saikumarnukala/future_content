"""
Main Orchestrator for the AI YouTube Shorts Factory.
"""

import json
import logging
from datetime import date
from pathlib import Path
from groq import Groq

from config.settings import settings
from pipeline.database import init_db, get_db, Video
from pipeline.topic_generator import generate_topic
from pipeline.script_generator import generate_script
from pipeline.voice_generator import generate_voice
from pipeline.image_generator import generate_scene_images
from pipeline.music_selector import select_background_music
from pipeline.caption_generator import generate_captions
from pipeline.video_creator import create_video
from pipeline.quality_controller import run_quality_control
from pipeline.youtube_uploader import upload_short
from pipeline.notifier import notify_slack

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_pipeline():
    """Run the complete pipeline to generate one Short."""
    init_db()
    db = next(get_db())
    
    run_date_str = date.today().isoformat()
    output_dir = settings.output_dir / run_date_str
    output_dir.mkdir(parents=True, exist_ok=True)
    
    max_attempts = 3
    client = Groq(api_key=settings.groq_api_key.get_secret_value())
    
    video_record = db.query(Video).filter(Video.run_date == date.today()).first()
    if not video_record:
        video_record = Video(run_date=date.today())
        db.add(video_record)
        db.commit()
        db.refresh(video_record)
        
    if video_record.upload_status == 'uploaded':
        logger.info("Video already uploaded for today.")
        return

    while video_record.attempt_count < max_attempts:
        video_record.attempt_count += 1
        db.commit()
        
        try:
            logger.info(f"--- Attempt {video_record.attempt_count} ---")
            
            # Topic Generation
            if not video_record.topic:
                topic, genre = generate_topic(db, client)
                video_record.topic = topic
                video_record.genre = genre
                db.commit()
                logger.info(f"Generated Topic: {topic}")
                
            # Script Generation
            if not video_record.script_json:
                from pipeline.topic_generator import get_recent_topics
                recent = get_recent_topics(db)
                script_data = generate_script(video_record.topic, recent)
                video_record.script_json = json.dumps(script_data)
                video_record.title = script_data.get("title", "")
                video_record.narration_text = script_data.get("full_narration", "")
                
                script_path = output_dir / "script.json"
                with open(script_path, "w") as f:
                    json.dump(script_data, f, indent=2)
                db.commit()
                logger.info("Generated Script")
            else:
                script_data = json.loads(video_record.script_json)
                
            # Voice Generation
            narration_path = output_dir / "narration.wav"
            if not narration_path.exists():
                generate_voice(video_record.narration_text, narration_path)
                video_record.narration_path = str(narration_path)
                db.commit()
                logger.info("Generated Voice")
                
            # Image Generation
            if not video_record.image_paths:
                image_paths = generate_scene_images(script_data, output_dir)
                video_record.image_paths = json.dumps(image_paths)
                db.commit()
                logger.info("Generated Images")
            else:
                image_paths = json.loads(video_record.image_paths)
                
            # Music Selection
            music_path = output_dir / "background.mp3"
            if not music_path.exists():
                select_background_music(music_path)
                video_record.music_file = str(music_path)
                db.commit()
                logger.info("Selected Music")
                
            # Caption Generation
            srt_path = output_dir / "captions.srt"
            ass_path = output_dir / "captions.ass"
            if not ass_path.exists():
                generate_captions(narration_path, output_dir)
                logger.info("Generated Captions")
                
            # Video Creation
            video_path = output_dir / "final_short.mp4"
            if not video_path.exists() or video_record.attempt_count > 1:
                create_video(
                    image_paths=image_paths,
                    narration_path=str(narration_path),
                    music_path=str(music_path),
                    ass_path=str(ass_path),
                    output_path=str(video_path),
                    script_data=script_data
                )
                video_record.video_path = str(video_path)
                db.commit()
                logger.info("Created Final Video")
                
            # Quality Control
            qc_results = run_quality_control(script_data, str(narration_path), str(video_path))
            video_record.quality_score = qc_results["overall"]
            video_record.qc_breakdown = json.dumps(qc_results)
            db.commit()
            
            logger.info(f"QC Score: {qc_results['overall']}")
            
            if qc_results["overall"] >= 90:
                logger.info("QC Passed. Proceeding to Upload.")
            elif qc_results["overall"] >= 80:
                logger.warning("QC Marginal. Flagging for review but uploading.")
                video_record.upload_status = 'review'
                notify_slack(f"Video created with marginal QC score: {qc_results['overall']}")
            else:
                logger.error(f"QC Failed: {qc_results['overall']}. Regenerating.")
                video_record.script_json = ""
                video_record.image_paths = ""
                continue
                
            # YouTube Upload (Temporarily skipped for local testing)
            if video_record.upload_status in ['pending', 'review']:
                logger.info("Skipping YouTube upload for local test run.")
                video_record.upload_status = 'local_test_complete'
                db.commit()
                
            break 
            
        except Exception as e:
            logger.error(f"Attempt {video_record.attempt_count} failed: {e}")
            video_record.error_log = str(e)
            db.commit()
            if video_record.attempt_count == max_attempts:
                notify_slack(f"Pipeline failed completely after {max_attempts} attempts: {e}", is_error=True)
                raise e

if __name__ == "__main__":
    run_pipeline()
