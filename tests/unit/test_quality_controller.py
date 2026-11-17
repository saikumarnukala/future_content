from unittest.mock import patch

from pipeline.quality_controller import run_quality_control, score_production, score_script


def test_score_script():
    script = {
        "hook": "short hook",
        "scenes": [{} for _ in range(6)],
        "full_narration": "word " * 100,
    }
    assert score_script(script) == 25


@patch("pipeline.quality_controller.analyze_audio", return_value={"duration": 30.0})
@patch("pipeline.quality_controller.score_production", return_value=25)
def test_run_quality_control(mock_production, mock_audio):
    script = {
        "hook": "h",
        "scenes": [{"visual_description": "A detailed shot"} for _ in range(6)],
        "full_narration": "w " * 90,
    }
    result = run_quality_control(script, "narration.wav", "video.mp4")
    assert result["overall"] == 100


def test_production_rejects_existing_invalid_file(tmp_path):
    output = tmp_path / "broken.mp4"
    output.write_text("not a video")
    assert score_production(str(output)) == 0
