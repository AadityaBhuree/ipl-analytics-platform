import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.predictor import ScorePredictor


@pytest.fixture(scope="module")
def predictor():
    """Module-scoped fixture to load the ML predictor once."""
    p = ScorePredictor()
    assert p.is_ready(), "Model files must be present and loaded"
    return p


def test_predictor_is_ready(predictor):
    assert predictor.is_ready() is True
    assert predictor.model is not None
    assert predictor.preprocessor is not None


def test_prediction_output_structure(predictor):
    res = predictor.predict(
        batting_team="Chennai Super Kings",
        bowling_team="Kolkata Knight Riders",
        venue="Eden Gardens",
        overs=20,
        year=2024,
    )
    assert isinstance(res, dict)
    assert "predicted_score" in res
    assert "predicted_score_range" in res
    assert "confidence" in res
    assert "input" in res

    score = res["predicted_score"]
    score_range = res["predicted_score_range"]
    assert isinstance(score, int)
    assert 50 <= score <= 320
    assert score_range["min"] == score - 20
    assert score_range["max"] == score + 20


@pytest.mark.parametrize("overs", [5, 10, 15, 20])
def test_prediction_scaling_with_overs(predictor, overs):
    res = predictor.predict(
        batting_team="Mumbai Indians",
        bowling_team="Delhi Capitals",
        venue="Wankhede Stadium",
        overs=overs,
        year=2024,
    )
    assert res["predicted_score"] > 0


def test_prediction_historical_year(predictor):
    res_2020 = predictor.predict(
        batting_team="Royal Challengers Bangalore",
        bowling_team="Sunrisers Hyderabad",
        venue="M Chinnaswamy Stadium",
        overs=20,
        year=2020,
    )
    assert res_2020["predicted_score"] > 0
    assert res_2020["input"]["year"] == 2020


def test_confidence_values(predictor):
    res = predictor.predict(
        batting_team="Rajasthan Royals",
        bowling_team="Punjab Kings",
        venue="Sawai Mansingh Stadium",
        overs=20,
    )
    assert res["confidence"] in ["high", "medium"]
