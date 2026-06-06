import pytest
from unittest.mock import patch
from pipeline.video_creator import create_video

@patch('pipeline.video_creator.subprocess.run')
def test_create_video(mock_run):
    images = ["i1.png", "i2.png", "i3.png", "i4.png", "i5.png", "i6.png"]
    script = {"scenes": [{} for _ in range(6)]}
    
    create_video(images, "narration.wav", "music.mp3", "captions.ass", "out.mp4", script)
    
    # 6 clips + 1 merge + 1 final = 8 calls to FFmpeg
    assert mock_run.call_count == 8
