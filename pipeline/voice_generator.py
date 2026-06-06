"""
Voice generation and audio post-processing using Deepgram Aura-2 and FFmpeg.
"""

import os
import requests
import subprocess
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_voice(text: str, output_path: Path, speed: float = 0.94):
    """
    Generate TTS using Deepgram Aura-2 via REST API.
    Saves temporary mp3, then processes it via FFmpeg to a final WAV.
    """
    url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en&encoding=mp3"
    headers = {
        "Authorization": f"Token {settings.deepgram_api_key.get_secret_value()}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    
    temp_mp3 = output_path.with_suffix('.temp.mp3')
    
    response = requests.post(url, headers=headers, json=payload)
    if not response.ok:
        print(f"Deepgram Primary Error: {response.text}")
        # Fallback
        url = "https://api.deepgram.com/v1/speak?model=aura-luna-en&encoding=mp3"
        response = requests.post(url, headers=headers, json=payload)
        if not response.ok:
            print(f"Deepgram Fallback Error: {response.text}")
        response.raise_for_status()
        
    with open(temp_mp3, "wb") as f:
        f.write(response.content)

    # Post-processing using FFmpeg (Removed aecho for clarity)
    filter_chain = (
        "acompressor=threshold=-20dB:ratio=3,"
        "highpass=f=80,"
        "loudnorm=I=-14:LRA=11:TP=-1.0"
    )
    
    cmd = [
        "ffmpeg", "-y", "-i", str(temp_mp3),
        "-af", filter_chain,
        "-ar", "48000", "-ac", "2",
        str(output_path)
    ]
    
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Cleanup temp
    if temp_mp3.exists():
        temp_mp3.unlink()
