import pytest
from unittest.mock import patch
from pathlib import Path
from pipeline.voice_generator import generate_voice

@patch('pipeline.voice_generator.subprocess.run')
@patch('pipeline.voice_generator.DeepgramClient')
def test_generate_voice(mock_deepgram, mock_subprocess, tmp_path):
    mock_client = mock_deepgram.return_value
    mock_client.speak.rest.v.return_value.save.return_value = None
    
    out_path = tmp_path / "out.wav"
    generate_voice("Hello world", out_path)
    
    mock_subprocess.assert_called_once()
    assert mock_client.speak.rest.v.called
