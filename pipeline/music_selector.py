"""
Music selector module. Currently falls back to local curated library.
"""

import random
import shutil
import subprocess
from pathlib import Path
from config.settings import settings

def select_background_music(output_path: Path) -> str:
    """
    Select background music from local curated library.
    Copies the selected file to the output path.
    Returns the path to the selected music.
    """
    valid_extensions = ['.mp3', '.wav']
    music_files = [
        f for f in settings.music_dir.iterdir()
        if f.is_file() and f.suffix.lower() in valid_extensions
    ]
    
    if not music_files:
        print("WARNING: No music found in local library. Creating silent track.")
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
            "-t", "35", str(output_path)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return str(output_path)
        
    selected = random.choice(music_files)
    shutil.copy2(selected, output_path)
    return str(output_path)
