import pytest
from unittest.mock import patch, MagicMock

@patch('pipeline.main.upload_short')
@patch('pipeline.main.run_quality_control')
@patch('pipeline.main.create_video')
@patch('pipeline.main.generate_captions')
@patch('pipeline.main.select_background_music')
@patch('pipeline.main.generate_scene_images')
@patch('pipeline.main.generate_voice')
@patch('pipeline.main.generate_script')
@patch('pipeline.main.generate_topic')
def test_full_pipeline_mocked(mock_topic, mock_script, mock_voice, mock_images, mock_music, mock_captions, mock_video, mock_qc, mock_upload):
    from pipeline.main import run_pipeline
    
    mock_topic.return_value = ("Test Topic", "Test Genre")
    mock_script.return_value = {"title": "Test"}
    mock_images.return_value = ["img1.png", "img2.png", "img3.png", "img4.png", "img5.png", "img6.png"]
    mock_qc.return_value = {"overall": 95}
    mock_upload.return_value = "xyz123"
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from pipeline.database import Base, get_db
    
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        yield db
        db.close()
        
    with patch('pipeline.main.get_db', side_effect=override_get_db), \
         patch('pipeline.main.init_db'):
         run_pipeline()
         
    mock_upload.assert_called_once()
