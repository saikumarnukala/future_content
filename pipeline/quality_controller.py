"""
Quality Control scoring engine.
"""

import json
import subprocess

def analyze_audio(narration_path: str) -> dict:
    """Analyze audio duration using FFprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", narration_path
    ]
    duration_str = subprocess.check_output(cmd).decode().strip()
    return {"duration": float(duration_str) if duration_str else 0}

def score_script(script_data: dict, client=None) -> int:
    """Score script quality on 0-25."""
    score = 25
    hook = script_data.get("hook", "")
    if len(hook.split()) > 10:
        score -= 2 # Penalty for long hook
    scenes = script_data.get("scenes", [])
    if len(scenes) != 6:
        score -= 10
    
    total_words = len(script_data.get("full_narration", "").split())
    if not (80 <= total_words <= 120):
        score -= 5
        
    return max(0, score)

def score_visuals(script_data: dict) -> int:
    """Score visual prompts."""
    score = 25
    scenes = script_data.get("scenes", [])
    for scene in scenes:
        if len(scene.get("visual_description", "")) < 10:
            score -= 2 # Penalty for vague descriptions
    return max(0, score)

def score_narration(narration_path: str) -> int:
    """Score audio quality and duration."""
    score = 25
    audio_stats = analyze_audio(narration_path)
    if not (26 <= audio_stats["duration"] <= 32):
        score -= 5 # Penalty for bad duration
    return max(0, score)

def score_production(video_path: str) -> int:
    """Score video production output."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", video_path],
            check=True, capture_output=True, text=True, timeout=30,
        )
        media = json.loads(result.stdout)
        duration = float(media["format"]["duration"])
    except (OSError, subprocess.SubprocessError, ValueError, KeyError):
        return 0

    has_audio = any(stream["codec_type"] == "audio" for stream in media["streams"])
    has_vertical_video = any(
        stream["codec_type"] == "video"
        and stream.get("width", 0) > 0
        and stream.get("height", 0) * 9 == stream["width"] * 16
        for stream in media["streams"]
    )
    return 25 if has_audio and has_vertical_video and 0 < duration <= 60 else 0

def run_quality_control(script_data: dict, narration_path: str, video_path: str) -> dict:
    """
    Run full QC scoring.
    """
    script_score = score_script(script_data)
    visual_score = score_visuals(script_data)
    audio_score = score_narration(narration_path)
    prod_score = score_production(video_path)
    
    total = script_score + visual_score + audio_score + prod_score
    
    return {
        "overall": total,
        "script": script_score,
        "visuals": visual_score,
        "narration": audio_score,
        "production": prod_score
    }
