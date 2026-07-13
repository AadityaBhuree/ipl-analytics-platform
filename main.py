from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn
import logging
import os
from dotenv import load_dotenv

load_dotenv()

from model.trainer import ModelTrainer
from model.predictor import ScorePredictor

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IPL Score Prediction API",
    description="Machine Learning backend for predicting IPL match scores",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Security for /train endpoint
API_KEY = os.getenv("API_KEY", "default_secret_key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=401, detail="Invalid or missing API Key"
        )
    return api_key

# Global state management attached to FastAPI app instance
@app.on_event("startup")
def load_model():
    app.state.predictor = ScorePredictor()
    app.state.trainer = ModelTrainer()
    app.state.is_training = False
    logger.info("IPL Score Predictor started and model state initialized.")

# Dependency to safely inject predictor
def get_predictor() -> ScorePredictor:
    predictor = getattr(app.state, "predictor", None)
    if not predictor or not predictor.is_ready():
        raise HTTPException(
            status_code=400,
            detail="Model not trained. Call /train first."
        )
    return predictor


class PredictionRequest(BaseModel):
    batting_team: str = Field(..., min_length=1)
    bowling_team: str = Field(..., min_length=1)
    venue: str = Field(..., min_length=1)
    overs: int = Field(default=20, ge=1, le=20)
    year: int = Field(default=2024, ge=2008, le=2100)


class PredictionResponse(BaseModel):
    predicted_score: int
    predicted_score_range: dict
    confidence: str
    input: dict


def train_and_reload():
    try:
        logger.info("Starting background training...")
        metrics = app.state.trainer.train()
        logger.info(f"Training completed successfully. Metrics: {metrics}")
        
        # Reload predictor safely
        logger.info("Reloading predictor with new model...")
        app.state.predictor = ScorePredictor()
    except Exception as e:
        logger.error(f"Background training failed: {str(e)}")
    finally:
        app.state.is_training = False


@app.get("/")
def root():
    return {"message": "IPL Score Prediction API", "status": "running"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_ready": getattr(app.state, "predictor", ScorePredictor()).is_ready(),
        "is_training": getattr(app.state, "is_training", False)
    }


@app.post("/train")
def trigger_training(
    background_tasks: BackgroundTasks, 
    api_key: str = Depends(get_api_key)
):
    if getattr(app.state, "is_training", False):
        raise HTTPException(
            status_code=400, detail="Training is already in progress."
        )
    
    app.state.is_training = True
    background_tasks.add_task(train_and_reload)
    
    return {
        "status": "accepted",
        "message": "Model training has been started in the background."
    }


@app.post("/predict", response_model=PredictionResponse)
def predict_score(request: PredictionRequest, predictor: ScorePredictor = Depends(get_predictor)):
    try:
        result = predictor.predict(
            batting_team=request.batting_team,
            bowling_team=request.bowling_team,
            venue=request.venue,
            overs=request.overs,
            year=request.year
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during prediction.")


@app.get("/teams")
def get_teams(predictor: ScorePredictor = Depends(get_predictor)):
    # Returns immediately in O(1) instead of reloading 100MB CSV
    try:
        return {
            "teams": list(predictor.preprocessor.team_encoder.classes_),
            "venues": list(predictor.preprocessor.venue_encoder.classes_)
        }
    except Exception as e:
        logger.error(f"Error fetching teams: {str(e)}")
        raise HTTPException(status_code=500, detail="Unable to retrieve teams.")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
