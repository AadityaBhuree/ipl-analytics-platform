import numpy as np
from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).parent.parent / "models" / "score_model.pkl"
ENCODERS_PATH = Path(__file__).parent.parent / "models" / "encoders.pkl"


class ScorePredictor:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self._load()

    def _load(self):
        if MODEL_PATH.exists() and ENCODERS_PATH.exists():
            self.model = joblib.load(MODEL_PATH)
            from model.preprocessor import DataPreprocessor
            self.preprocessor = DataPreprocessor()
            self.preprocessor.load_encoders(ENCODERS_PATH)

    def predict(self, batting_team: str, bowling_team: str, venue: str, overs: int = 20, year: int = 2024):
        if self.model is None or self.preprocessor is None:
            raise ValueError("Model not loaded. Train the model first.")

        features = self.preprocessor.get_team_stats(batting_team, bowling_team, venue, year)
        features['overs'] = overs

        feature_names = [
            'batting_team_enc', 'bowling_team_enc', 'venue_enc', 'city_enc',
            'overs', 'year', 'avg_runs', 'std_runs', 'max_runs', 'avg_wickets', 'opp_avg_runs'
        ]

        X = np.array([[features[col] for col in feature_names]])

        prediction = self.model.predict(X)[0]

        confidence = self._get_confidence(features)

        return {
            'predicted_score': round(prediction),
            'predicted_score_range': {
                'min': round(prediction - 20),
                'max': round(prediction + 20)
            },
            'confidence': confidence,
            'input': {
                'batting_team': batting_team,
                'bowling_team': bowling_team,
                'venue': venue,
                'overs': overs,
                'year': year
            }
        }

    def _get_confidence(self, features):
        avg_runs = features.get('avg_runs', 150)
        if avg_runs > 0:
            return "high"
        return "medium"

    def is_ready(self):
        return self.model is not None and self.preprocessor is not None
