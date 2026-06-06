"""
Caption generation using Deepgram ASR for timestamps and generating SRT/ASS files.
"""

import requests
from pathlib import Path
from config.settings import settings
from config.ffmpeg_filters import ASS_HEADER

def generate_captions(audio_path: Path, output_dir: Path) -> tuple[Path, Path]:
    """
    Transcribe audio to get word-level timestamps, then create SRT and ASS files.
    """
    url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&punctuate=true"
    headers = {
        "Authorization": f"Token {settings.deepgram_api_key.get_secret_value()}",
        "Content-Type": "audio/wav"
    }
    
    with open(audio_path, "rb") as f:
        audio_data = f.read()
        
    response = requests.post(url, headers=headers, data=audio_data)
    response.raise_for_status()
    
    data = response.json()
    
    words = []
    try:
        words_data = data["results"]["channels"][0]["alternatives"][0]["words"]
        # Convert dict back to a simple object-like struct to match existing code logic
        class WordObj:
            def __init__(self, w):
                self.word = w["word"]
                self.start = w["start"]
                self.end = w["end"]
        words = [WordObj(w) for w in words_data]
    except (KeyError, IndexError):
        print("Warning: Could not parse words from Deepgram response.")
        
    srt_path = output_dir / "captions.srt"
    ass_path = output_dir / "captions.ass"
    
    _generate_srt(words, srt_path)
    _generate_ass(words, ass_path)
    
    return srt_path, ass_path

def format_time_srt(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

def format_time_ass(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int((seconds - int(seconds)) * 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"

def _chunk_words(words: list, chunk_size: int = 2) -> list:
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(words[i:i + chunk_size])
    return chunks

def _generate_srt(words: list, srt_path: Path):
    chunks = _chunk_words(words, 2)
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks, 1):
            if not chunk: continue
            start = chunk[0].start
            end = chunk[-1].end
            text = " ".join(w.word for w in chunk)
            
            f.write(f"{i}\n")
            f.write(f"{format_time_srt(start)} --> {format_time_srt(end)}\n")
            f.write(f"{text}\n\n")

def _generate_ass(words: list, ass_path: Path):
    chunks = _chunk_words(words, 2)
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ASS_HEADER)
        for chunk in chunks:
            if not chunk: continue
            start = chunk[0].start
            end = chunk[-1].end
            
            ass_line_text = " ".join(w.word for w in chunk)
                
            f.write(f"Dialogue: 0,{format_time_ass(start)},{format_time_ass(end)},Default,,0,0,0,,{ass_line_text}\n")
