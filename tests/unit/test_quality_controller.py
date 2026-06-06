import pytest
from unittest.mock import patch, MagicMock
from pipeline.quality_controller import run_quality_control, score_script

def test_score_script():
    script = {
        "hook": "short hook",
        "scenes": [{} for _ in range(6)],
        "full_narration": "word " * 100
    }
    mock_client = MagicMock()
    score = score_script(script, mock_client)
    assert score == 25

@patch('pipeline.quality_controller.analyze_audio')
@patch('pipeline.quality_controller.os.path.exists')
def test_run_quality_control(mock_exists, mock_audio):
    mock_exists.return_value = True
    mock_audio.return_value = {"duration": 30.0}
    
    script = {"hook": "h", "scenes": [{} for _ in range(6)], "full_narration": "w " * 90}
    
    res = run_quality_control(script, "narration.wav", "video.mp4")
    assert res["overall"] == 100
