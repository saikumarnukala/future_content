from unittest.mock import patch, MagicMock
from pipeline.image_generator import generate_scene_images, generate_image_cloudflare

@patch('pipeline.image_generator.requests.post')
def test_generate_image_cloudflare(mock_post, tmp_path):
    mock_response = MagicMock()
    mock_response.content = b"testdata"
    mock_post.return_value = mock_response
    
    out = tmp_path / "img.png"
    generate_image_cloudflare("Test prompt", out)
    assert out.read_bytes() == b"testdata"

@patch('pipeline.image_generator.time.sleep')
@patch('pipeline.image_generator.generate_image_cloudflare')
def test_generate_scene_images(mock_gen, mock_sleep, tmp_path):
    script = {"scenes": [{"visual_description": "v1"}, {"visual_description": "v2"}, {"visual_description": "v3"}, {"visual_description": "v4"}, {"visual_description": "v5"}, {"visual_description": "v6"}]}
    paths = generate_scene_images(script, tmp_path)
    assert len(paths) == 6
    assert mock_gen.call_count == 6
