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
        self.team_stats_cache = {}
        self.bowl_stats_cache = {}
        self.venue_city_map = {}
        self.global_stats = {}
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
            self.global_stats = {
                'avg_runs': float(df['avg_runs'].mean()) if not df['avg_runs'].isna().all() else 150.0,
                'std_runs': float(df['std_runs'].mean()) if not df['std_runs'].isna().all() else 30.0,
                'max_runs': float(df['max_runs'].mean()) if not df['max_runs'].isna().all() else 220.0,
                'avg_wickets': float(df['avg_wickets'].mean()) if not df['avg_wickets'].isna().all() else 5.0,
                'opp_avg_runs': float(df['opp_avg_runs'].mean()) if not df['opp_avg_runs'].isna().all() else 150.0
            }

            all_teams = pd.concat([df['batting_team'], df['bowling_team']]).unique()
            all_venues = df['venue'].unique()
            all_cities = df['city'].unique()

            self.team_encoder.fit(all_teams)
            self.venue_encoder.fit(all_venues)
            self.city_encoder.fit(all_cities)
            
            # Cache statistics for O(1) inference
            self.venue_city_map = dict(zip(df['venue'], df['city']))
            self.team_stats_cache = {}
            for _, row in df.drop_duplicates('batting_team').iterrows():
                self.team_stats_cache[row['batting_team']] = {
                    'avg_runs': row['avg_runs'],
                    'std_runs': row['std_runs'],
                    'max_runs': row['max_runs'],
                    'avg_wickets': row['avg_wickets']
                }
            
            self.bowl_stats_cache = {}
            for _, row in df.drop_duplicates('bowling_team').iterrows():
                self.bowl_stats_cache[row['bowling_team']] = {
                    'opp_avg_runs': row['opp_avg_runs']
                }

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
            raise ValueError("Preprocessor is not fitted. Load encoders first.")

        # Fail explicitly on unknown inputs instead of masking errors
        if batting_team not in self.team_encoder.classes_:
            raise ValueError(f"Unknown batting team: {batting_team}")
        if bowling_team not in self.team_encoder.classes_:
            raise ValueError(f"Unknown bowling team: {bowling_team}")
        if venue not in self.venue_encoder.classes_:
            raise ValueError(f"Unknown venue: {venue}")

        bt_enc = self.team_encoder.transform([batting_team])[0]
        bowl_enc = self.team_encoder.transform([bowling_team])[0]
        v_enc = self.venue_encoder.transform([venue])[0]
        
        city = self.venue_city_map.get(venue, self.city_encoder.classes_[0])
        c_enc = self.city_encoder.transform([city])[0]

        # O(1) dictionary lookup instead of O(N) DataFrame processing
        b_stats = self.team_stats_cache.get(batting_team, {
            'avg_runs': self.global_stats.get('avg_runs', 150.0),
            'std_runs': self.global_stats.get('std_runs', 30.0),
            'max_runs': self.global_stats.get('max_runs', 220.0),
            'avg_wickets': self.global_stats.get('avg_wickets', 5.0)
        })
        
        bw_stats = self.bowl_stats_cache.get(bowling_team, {
            'opp_avg_runs': self.global_stats.get('opp_avg_runs', 150.0)
        })

        return {
            'batting_team_enc': bt_enc,
            'bowling_team_enc': bowl_enc,
            'venue_enc': v_enc,
            'city_enc': c_enc,
            'overs': 20,
            'year': year,
            'avg_runs': b_stats['avg_runs'],
            'std_runs': b_stats['std_runs'],
            'max_runs': b_stats['max_runs'],
            'avg_wickets': b_stats['avg_wickets'],
            'opp_avg_runs': bw_stats['opp_avg_runs']
        }

    def save_encoders(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            'team_encoder': self.team_encoder,
            'venue_encoder': self.venue_encoder,
            'city_encoder': self.city_encoder,
            'team_stats_cache': self.team_stats_cache,
            'bowl_stats_cache': self.bowl_stats_cache,
            'venue_city_map': self.venue_city_map,
            'global_stats': self.global_stats
        }, path)

    def load_encoders(self, path: Path):
        data = joblib.load(path)
        self.team_encoder = data['team_encoder']
        self.venue_encoder = data['venue_encoder']
        self.city_encoder = data['city_encoder']
        self.team_stats_cache = data.get('team_stats_cache', {})
        self.bowl_stats_cache = data.get('bowl_stats_cache', {})
        self.venue_city_map = data.get('venue_city_map', {})
        self.global_stats = data.get('global_stats', {})
        self._fitted = True
