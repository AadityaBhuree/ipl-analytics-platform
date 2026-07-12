import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import joblib
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "IPL.csv"

class DataPreprocessor:
    def __init__(self):
        self.team_encoder = LabelEncoder()
        self.venue_encoder = LabelEncoder()
        self.city_encoder = LabelEncoder()
        self._fitted = False

    def load_data(self):
        df = pd.read_csv(DATA_PATH)
        return df

    def engineer_features(self, df):
        match_level = df.groupby('match_id').agg({
            'team_runs': 'max',
            'team_balls': 'max',
            'team_wicket': 'max',
            'batting_team': 'first',
            'bowling_team': 'first',
            'venue': 'first',
            'city': 'first',
            'overs': 'max',
            'year': 'first'
        }).reset_index()

        team_stats = match_level.groupby('batting_team').agg({
            'team_runs': ['mean', 'std', 'max'],
            'team_wicket': 'mean'
        }).reset_index()
        team_stats.columns = ['batting_team', 'avg_runs', 'std_runs', 'max_runs', 'avg_wickets']

        match_level = match_level.merge(team_stats, on='batting_team', how='left')

        bowl_stats = match_level.groupby('bowling_team').agg({
            'team_runs': 'mean'
        }).reset_index()
        bowl_stats.columns = ['bowling_team', 'opp_avg_runs']

        match_level = match_level.merge(bowl_stats, on='bowling_team', how='left')

        return match_level

    def prepare_data(self, df=None):
        if df is None:
            df = self.load_data()

        df = self.engineer_features(df)

        if not self._fitted:
            all_teams = pd.concat([df['batting_team'], df['bowling_team']]).unique()
            all_venues = df['venue'].unique()
            all_cities = df['city'].unique()

            self.team_encoder.fit(all_teams)
            self.venue_encoder.fit(all_venues)
            self.city_encoder.fit(all_cities)
            self._fitted = True

        df['batting_team_enc'] = self.team_encoder.transform(df['batting_team'])
        df['bowling_team_enc'] = self.team_encoder.transform(df['bowling_team'])
        df['venue_enc'] = self.venue_encoder.transform(df['venue'])
        df['city_enc'] = self.city_encoder.transform(df['city'])

        feature_cols = [
            'batting_team_enc', 'bowling_team_enc', 'venue_enc', 'city_enc',
            'overs', 'year', 'avg_runs', 'std_runs', 'max_runs', 'avg_wickets', 'opp_avg_runs'
        ]

        df = df.dropna(subset=feature_cols + ['team_runs'])

        X = df[feature_cols]
        y = df['team_runs']

        return X, y, self

    def get_team_stats(self, batting_team: str, bowling_team: str, venue: str, year: int = 2024):
        if not self._fitted:
            self.prepare_data()

        try:
            bt_enc = self.team_encoder.transform([batting_team])[0]
        except:
            bt_enc = 0

        try:
            bowl_enc = self.team_encoder.transform([bowling_team])[0]
        except:
            bowl_enc = 0

        try:
            v_enc = self.venue_encoder.transform([venue])[0]
        except:
            v_enc = 0

        df = self.load_data()
        match_level = self.engineer_features(df)

        team_row = match_level[match_level['batting_team'] == batting_team]
        if len(team_row) > 0:
            avg_runs = team_row['avg_runs'].iloc[0]
            std_runs = team_row['std_runs'].iloc[0]
            max_runs = team_row['max_runs'].iloc[0]
            avg_wickets = team_row['avg_wickets'].iloc[0]
        else:
            avg_runs, std_runs, max_runs, avg_wickets = 150, 30, 220, 5

        bowl_row = match_level[match_level['bowling_team'] == bowling_team]
        if len(bowl_row) > 0:
            opp_avg_runs = bowl_row['opp_avg_runs'].iloc[0]
        else:
            opp_avg_runs = 150

        return {
            'batting_team_enc': bt_enc,
            'bowling_team_enc': bowl_enc,
            'venue_enc': v_enc,
            'city_enc': v_enc,
            'overs': 20,
            'year': year,
            'avg_runs': avg_runs,
            'std_runs': std_runs,
            'max_runs': max_runs,
            'avg_wickets': avg_wickets,
            'opp_avg_runs': opp_avg_runs
        }

    def save_encoders(self, path: Path):
        joblib.dump({
            'team_encoder': self.team_encoder,
            'venue_encoder': self.venue_encoder,
            'city_encoder': self.city_encoder
        }, path)

    def load_encoders(self, path: Path):
        data = joblib.load(path)
        self.team_encoder = data['team_encoder']
        self.venue_encoder = data['venue_encoder']
        self.city_encoder = data['city_encoder']
        self._fitted = True
