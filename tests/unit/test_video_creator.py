from unittest.mock import patch
from pipeline.video_creator import create_video

@patch('pipeline.video_creator.subprocess.run')
def test_create_video(mock_run):
    mock_run.return_value.stdout = "30.0"
    images = ["i1.png", "i2.png", "i3.png", "i4.png", "i5.png", "i6.png"]
    script = {"scenes": [{} for _ in range(6)]}
    
    create_video(images, "narration.wav", "music.mp3", "captions.ass", "out.mp4", script)
    
    assert mock_run.call_args_list[0].args[0][0] == "ffprobe"
    assert mock_run.call_args_list[-1].args[0][-1] == "out.mp4"
