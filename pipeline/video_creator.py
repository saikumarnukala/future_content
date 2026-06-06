"""
FFmpeg pipeline for video creation.
"""

import subprocess
import os
from pathlib import Path
from config.ffmpeg_filters import MOTION_FILTERS, TRANSITION_DURATION, MUSIC_VOLUME_FILTER

def get_audio_duration(path: str) -> float:
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())

def create_video(
    image_paths: list[str],
    narration_path: str,
    music_path: str,
    ass_path: str,
    output_path: str,
    script_data: dict
):
    """
    Assemble the final video using FFmpeg complex filtergraphs.
    """
    scenes = script_data.get("scenes", [])
    
    if len(image_paths) != len(scenes):
        raise ValueError(f"Number of images ({len(image_paths)}) must match number of scenes ({len(scenes)})")

    audio_duration = get_audio_duration(narration_path)
    # Add 1.5s padding so the audio finishes completely before fading out
    total_target_duration = audio_duration + 1.5
    
    N = len(image_paths)
    clip_duration = (total_target_duration + (N - 1) * TRANSITION_DURATION) / N

    # Step 1: Create individual video clips with motion
    clips = []
    temp_dir = Path(output_path).parent / "temp_clips"
    temp_dir.mkdir(exist_ok=True)
    
    for i, (img, scene) in enumerate(zip(image_paths, scenes)):
        camera_mov = scene.get("camera_movement", "static-wide")
        motion_filter = MOTION_FILTERS.get(camera_mov, MOTION_FILTERS["static-wide"])
        
        clip_path = temp_dir / f"clip_{i}.mp4"
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", img,
            "-vf", motion_filter,
            "-c:v", "libx264", "-t", f"{clip_duration:.3f}", "-pix_fmt", "yuv420p",
            str(clip_path)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        clips.append(str(clip_path))
        
    # Step 2: Concatenate with crossfades
    filter_complex = ""
    inputs = []
    for i, clip in enumerate(clips):
        inputs.extend(["-i", clip])
        
    offset = clip_duration - TRANSITION_DURATION
    last_out = "[0:v]"
    
    for i in range(1, N):
        next_in = f"[{i}:v]"
        out_lbl = f"[v{i}]" if i < N - 1 else "[vout]"
        filter_complex += f"{last_out}{next_in}xfade=transition=fade:duration={TRANSITION_DURATION}:offset={offset:.3f}{out_lbl};"
        last_out = out_lbl
        offset += clip_duration - TRANSITION_DURATION
        
    filter_complex = filter_complex.strip(";")
    
    merged_video = temp_dir / "merged.mp4"
    cmd_merge = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_complex, "-map", "[vout]", "-c:v", "libx264", str(merged_video)]
    subprocess.run(cmd_merge, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Step 3: Layer audio and burn captions
    escaped_ass = str(ass_path).replace('\\', '/').replace(':', '\\:') # Windows FFmpeg escaping
    
    final_complex = (
        f"[2:a]{MUSIC_VOLUME_FILTER}[a2];"
        f"[1:a]volume=1.0[a1];"
        f"[a1][a2]amix=inputs=2:duration=first:dropout_transition=2[aout];"
        f"[0:v]subtitles='{escaped_ass}'[vout]"
    )
    
    cmd_final = [
        "ffmpeg", "-y",
        "-i", str(merged_video),
        "-i", narration_path,
        "-i", music_path,
        "-filter_complex", final_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-crf", "18", "-preset", "slow",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{total_target_duration:.3f}",
        output_path
    ]
    
    subprocess.run(cmd_final, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Cleanup temp clips
    for clip in clips:
        Path(clip).unlink(missing_ok=True)
    merged_video.unlink(missing_ok=True)
