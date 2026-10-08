# 🏏 IPL Score Predictor Platform & Analytics API

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4%2B-F7931E.svg?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/Pytest-15%2F15%20Passing-success.svg)](tests/)
[![CI](https://github.com/AadityaBhuree/ipl-analytics-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/AadityaBhuree/ipl-analytics-platform/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](Dockerfile)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An asynchronous machine learning platform and RESTful microservice providing real-time ball-by-ball IPL score projections, venue telemetry, and match outcome probabilities. Features a **FastAPI** backend with asynchronous model retraining and a responsive **CustomTkinter** desktop client.

---

## 🚀 Key Features

* **Real-Time Score Forecasting:** Multi-feature regression model factoring batting team power, bowling suppression, historical venue run distributions, and innings progression.
* **Hardened Security:** Explicit `X-API-Key` authentication protecting administrative endpoints (`/train`); rejects unconfigured default keys with HTTP 500/401.
* **Asynchronous Retraining:** Utilizes FastAPI `BackgroundTasks` for non-blocking model re-fitting without interrupting incoming inference traffic.
* **Production Docker Container:** Multi-stage, unprivileged Python 3.11 container with healthcheck monitoring on `/health`.
* **100% Automated Pytest Suite:** 15 comprehensive unit tests covering API readiness, input boundaries, score constraints, and security authentication.

---

## 🔌 API Reference

### 1. `POST /predict`
Predicts the final innings total for an IPL match situation.

**Request Body:**
```json
{
  "batting_team": "Chennai Super Kings",
  "bowling_team": "Mumbai Indians",
  "venue": "Wankhede Stadium",
  "overs": 20,
  "year": 2024
}
```

**Response:**
```json
{
  "predicted_score": 182.4,
  "confidence": 0.85,
  "team_stats": {
    "avg_runs": 178.2,
    "std_runs": 14.6,
    "max_runs": 218.0
  }
}
```

### 2. `POST /train`
Triggers an asynchronous model retraining job using the latest match dataset. Requires `X-API-Key` header.

**Headers:**
`X-API-Key: <your_secret_api_key>`

### 3. `GET /health`
Checks server status and model readiness.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "uptime": "active"
}
```

---

## 🐳 Docker Deployment

Run the API service using Docker:

```bash
# Build the container image
docker build -t ipl-score-predictor .

# Run the container with a secure API key
docker run -d -p 8000:8000 \
  -e API_KEY="your_secure_api_key" \
  --name ipl_api ipl-score-predictor
```

API documentation will be accessible at **`http://localhost:8000/docs`**.

---

## 🧪 Testing

Execute the automated test suite with `pytest`:

```bash
pytest tests/ -v
```

All 15 automated test cases validate model readiness, boundary overs, prediction output schemas, confidence mapping, and secure retraining.
