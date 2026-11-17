from unittest.mock import patch

from pipeline.voice_generator import generate_voice


@patch("pipeline.voice_generator.subprocess.run")
@patch("pipeline.voice_generator.requests.post")
def test_generate_voice(mock_post, mock_subprocess, tmp_path):
    mock_post.return_value.ok = True
    mock_post.return_value.content = b"test audio"
    output = tmp_path / "out.wav"
    generate_voice("Hello world", output)

    mock_subprocess.assert_called_once()
    assert mock_post.call_args.kwargs["json"] == {"text": "Hello world"}
    assert not output.with_suffix(".temp.mp3").exists()
