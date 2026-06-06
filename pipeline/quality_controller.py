"""
Quality Control scoring engine.
"""

import os
import subprocess
from groq import Groq
from config.settings import settings

def analyze_audio(narration_path: str) -> dict:
    """Analyze audio duration using FFprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", narration_path
    ]
    duration_str = subprocess.check_output(cmd).decode().strip()
    return {"duration": float(duration_str) if duration_str else 0}

def score_script(script_data: dict, client: Groq) -> int:
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
    score = 25
    if not os.path.exists(video_path):
        return 0
    return score

def run_quality_control(script_data: dict, narration_path: str, video_path: str) -> dict:
    """
    Run full QC scoring.
    """
    client = Groq(api_key=settings.groq_api_key.get_secret_value())
    
    script_score = score_script(script_data, client)
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
