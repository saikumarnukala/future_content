import pytest
from unittest.mock import patch, MagicMock
from pipeline.youtube_uploader import upload_short

@patch('pipeline.youtube_uploader.get_youtube_service')
@patch('pipeline.youtube_uploader.MediaFileUpload')
def test_youtube_upload(mock_media, mock_get_service):
    mock_youtube = MagicMock()
    mock_get_service.return_value = mock_youtube
    
    mock_request = MagicMock()
    mock_request.execute.return_value = {"id": "123456"}
    mock_youtube.videos().insert.return_value = mock_request
    
    script = {"youtube_title": "T", "hashtags": ["#AI"]}
    vid = upload_short("vid.mp4", script)
    
    assert vid == "123456"
    assert mock_youtube.videos().insert.called
