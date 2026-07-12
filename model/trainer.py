from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from pathlib import Path
import numpy as np

from model.preprocessor import DataPreprocessor

MODEL_PATH = Path(__file__).parent.parent / "models" / "score_model.pkl"
ENCODERS_PATH = Path(__file__).parent.parent / "models" / "encoders.pkl"


class ModelTrainer:
    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.model = None

    def train(self):
        X, y, preprocessor = self.preprocessor.prepare_data()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            min_samples_split=5,
            random_state=42
        )

        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)

        metrics = {
            'mae': mean_absolute_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'r2': r2_score(y_test, y_pred)
        }

        cv_scores = cross_val_score(self.model, X, y, cv=5, scoring='neg_mean_absolute_error')
        metrics['cv_mae'] = -cv_scores.mean()

        self.save_model()
        preprocessor.save_encoders(ENCODERS_PATH)

        return metrics

    def save_model(self):
        joblib.dump(self.model, MODEL_PATH)

    def load_model(self):
        if MODEL_PATH.exists():
            self.model = joblib.load(MODEL_PATH)
            self.preprocessor.load_encoders(ENCODERS_PATH)
            return True
        return False

    def get_feature_importance(self):
        if self.model is None:
            return None

        feature_names = [
            'batting_team_enc', 'bowling_team_enc', 'venue_enc', 'city_enc',
            'overs', 'year', 'avg_runs', 'std_runs', 'max_runs', 'avg_wickets', 'opp_avg_runs'
        ]

        importance = self.model.feature_importances_
        return dict(zip(feature_names, importance.tolist()))
