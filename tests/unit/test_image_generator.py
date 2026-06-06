import pytest
import base64
from unittest.mock import patch, MagicMock
from pathlib import Path
from pipeline.image_generator import generate_scene_images, generate_image_together

@patch('pipeline.image_generator.requests.post')
def test_generate_image_together(mock_post, tmp_path):
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": [{"b64_json": base64.b64encode(b"testdata").decode()}]}
    mock_post.return_value = mock_response
    
    out = tmp_path / "img.png"
    generate_image_together("Test prompt", out)
    assert out.read_bytes() == b"testdata"

@patch('pipeline.image_generator.generate_image_together')
def test_generate_scene_images(mock_gen, tmp_path):
    script = {"scenes": [{"visual_description": "v1"}, {"visual_description": "v2"}, {"visual_description": "v3"}, {"visual_description": "v4"}, {"visual_description": "v5"}, {"visual_description": "v6"}]}
    paths = generate_scene_images(script, tmp_path)
    assert len(paths) == 6
    assert mock_gen.call_count == 6
