import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app


@pytest.fixture(scope="module")
def client():
    """Module-level TestClient fixture executing startup event handlers."""
    with TestClient(app) as c:
        yield c


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "IPL Score Prediction API", "status": "running"}


def test_read_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "healthy"
    assert "model_ready" in json_response
    assert "is_training" in json_response


def test_get_teams_and_venues(client):
    response = client.get("/teams")
    assert response.status_code == 200
    data = response.json()
    assert "teams" in data
    assert "venues" in data
    assert len(data["teams"]) > 0
    assert len(data["venues"]) > 0
    assert "Chennai Super Kings" in data["teams"]


def test_predict_endpoint_valid(client):
    payload = {
        "batting_team": "Chennai Super Kings",
        "bowling_team": "Mumbai Indians",
        "venue": "Wankhede Stadium",
        "overs": 20,
        "year": 2024,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_score" in data
    assert 50 <= data["predicted_score"] <= 300
    assert "predicted_score_range" in data
    assert data["predicted_score_range"]["min"] < data["predicted_score_range"]["max"]
    assert data["confidence"] in ["high", "medium", "low"]


def test_predict_endpoint_validation_errors(client):
    # Negative overs
    bad_payload = {
        "batting_team": "Chennai Super Kings",
        "bowling_team": "Mumbai Indians",
        "venue": "Wankhede Stadium",
        "overs": -5,
    }
    response = client.post("/predict", json=bad_payload)
    assert response.status_code == 422

    # Overs exceeding 20
    bad_overs_payload = {
        "batting_team": "Chennai Super Kings",
        "bowling_team": "Mumbai Indians",
        "venue": "Wankhede Stadium",
        "overs": 25,
    }
    response = client.post("/predict", json=bad_overs_payload)
    assert response.status_code == 422


def test_train_endpoint_unauthorized(client):
    # Missing API Key
    response = client.post("/train")
    assert response.status_code == 401

    # Invalid API Key
    response = client.post("/train", headers={"X-API-Key": "wrong_key_xyz"})
    assert response.status_code == 401


def test_train_endpoint_authorized(client, monkeypatch):
    import main
    monkeypatch.setattr(main, "API_KEY", "test_secure_key_123")
    response = client.post("/train", headers={"X-API-Key": "test_secure_key_123"})
    assert response.status_code == 200
    assert "status" in response.json()
