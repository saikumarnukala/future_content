import pytest
from unittest.mock import patch, MagicMock
from pipeline.script_generator import generate_script, validate_script

@patch('pipeline.script_generator.Groq')
def test_generate_script(mock_groq):
    mock_client = MagicMock()
    mock_groq.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"title": "Test", "hook": "Look here", "scenes": [{"scene_number":1,"duration_seconds":5,"narration":"word","visual_description":"desc","camera_movement":"static-wide","mood":"tense"},{"scene_number":2,"duration_seconds":5,"narration":"word","visual_description":"desc","camera_movement":"static-wide","mood":"tense"},{"scene_number":3,"duration_seconds":5,"narration":"word","visual_description":"desc","camera_movement":"static-wide","mood":"tense"},{"scene_number":4,"duration_seconds":5,"narration":"word","visual_description":"desc","camera_movement":"static-wide","mood":"tense"},{"scene_number":5,"duration_seconds":5,"narration":"word","visual_description":"desc","camera_movement":"static-wide","mood":"tense"},{"scene_number":6,"duration_seconds":5,"narration":"word","visual_description":"desc","camera_movement":"static-wide","mood":"tense"}], "full_narration": "' + 'word ' * 80 + '"}'
    mock_client.chat.completions.create.return_value = mock_response

    script = generate_script("AI Future", ["Past Topic"])
    assert script["title"] == "Test"
    assert len(script["scenes"]) == 6
