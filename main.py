from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

from model.trainer import ModelTrainer
from model.predictor import ScorePredictor

app = FastAPI(
    title="IPL Score Prediction API",
    description="Machine Learning backend for predicting IPL match scores",
    version="1.0.0"
)

predictor = ScorePredictor()
trainer = ModelTrainer()


class PredictionRequest(BaseModel):
    batting_team: str
    bowling_team: str
    venue: str
    overs: Optional[int] = 20
    year: Optional[int] = 2024


class PredictionResponse(BaseModel):
    predicted_score: int
    predicted_score_range: dict
    confidence: str
    input: dict


class TrainingResponse(BaseModel):
    status: str
    metrics: dict
    feature_importance: Optional[dict] = None


@app.get("/")
def root():
    return {"message": "IPL Score Prediction API", "status": "running"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_ready": predictor.is_ready()
    }


@app.post("/train", response_model=TrainingResponse)
def train_model():
    try:
        metrics = trainer.train()
        feature_importance = trainer.get_feature_importance()

        global predictor
        predictor = ScorePredictor()

        return TrainingResponse(
            status="success",
            metrics=metrics,
            feature_importance=feature_importance
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict", response_model=PredictionResponse)
def predict_score(request: PredictionRequest):
    if not predictor.is_ready():
        raise HTTPException(
            status_code=400,
            detail="Model not trained. Call /train first."
        )

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
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/teams")
def get_teams():
    from model.preprocessor import DataPreprocessor
    preprocessor = DataPreprocessor()
    preprocessor.prepare_data()

    return {
        "teams": list(preprocessor.team_encoder.classes_),
        "venues": list(preprocessor.venue_encoder.classes_)
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
