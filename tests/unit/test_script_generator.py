import json
from unittest.mock import MagicMock, patch

import pytest

from pipeline.script_generator import generate_script, validate_script


def script_response():
    return {
        "title": "Test",
        "hook": "Look here",
        "full_narration": "Unrelated model output",
        "scenes": [
            {
                "narration": f"Scene {index} has a unique line that belongs to this particular moment of the story.",
                "visual_description": f"Vertical frame showing event {index} in the story",
            }
            for index in range(6)
        ],
    }


@patch("pipeline.script_generator.Groq")
def test_generate_script_uses_scene_narration(mock_groq):
    data = script_response()
    response = MagicMock()
    response.choices[0].message.content = json.dumps(data)
    mock_groq.return_value.chat.completions.create.return_value = response
    script = generate_script("AI Future", ["Past Topic"])
    assert script["full_narration"] == " ".join(scene["narration"] for scene in data["scenes"])


def test_same_visual_cannot_pass_twice():
    data = script_response()
    data["scenes"][1]["visual_description"] = data["scenes"][0]["visual_description"]
    with pytest.raises(ValueError, match="distinct visual"):
        validate_script(data)
