import pandas as pd
import os
from sklearn.ensemble import RandomForestClassifier

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "archive")

races = pd.read_csv(os.path.join(DATA_DIR, "races.csv"))
results = pd.read_csv(os.path.join(DATA_DIR, "results.csv"))
driver_standings = pd.read_csv(os.path.join(DATA_DIR, "driver_standings.csv"))
drivers = pd.read_csv(os.path.join(DATA_DIR, "drivers.csv"))

drivers['full_name'] = drivers['forename'] + ' ' + drivers['surname']

def calculate_features(year, cutoff_race_id, results_df):
    """
    Calculates features for all drivers in a given season up to a given cutoff race.
    Features:
    - Total points
    - Total wins
    - Total podiums
    - Average finishing position
    - Total races
    """

    results_df['positionOrder'] = pd.to_numeric(results_df['positionOrder'], errors='coerce')
    
    driver_features = results_df[results_df['raceId'] <= cutoff_race_id].groupby('driverId').agg(
        total_points=('points', 'sum'),
        total_wins=('positionOrder', lambda x: (x == 1).sum()),
        total_podiums=('positionOrder', lambda x: (x <= 3).sum()),
        avg_finishing_position=('positionOrder', 'mean'),
        total_races=('raceId', 'nunique')
    ).reset_index()

    driver_features['avg_points'] = driver_features['total_points'] / driver_features['total_races']

    return driver_features


def create_training_set(races, results, driver_standings):
    """Creates the training set for the model from past seasons"""
    
    data = []
    for year in range(2018, 2024):  # Using data from 2018 to 2023 for training
        # --- FIX 4: Correct column name from race_id to raceId ---
        cutoff_race_id = races[races['year'] == year]['raceId'].max()
        features_for_year = calculate_features(year, cutoff_race_id, results)

        # find champion for the year
        final_race_id = races[races['year'] == year]['raceId'].max()
        champion_id = driver_standings[driver_standings['raceId'] == final_race_id].iloc[0]['driverId']

        features_for_year['champion'] = (features_for_year['driverId'] == champion_id).astype(int)

        data.append(features_for_year)

    return pd.concat(data, ignore_index=True)

def model_training():
    """Trains the model on the training set."""
    training_data = create_training_set(races, results, driver_standings)

    features = [
        'total_points',
        'total_wins',
        'total_podiums',
        'avg_finishing_position',
        'total_races'
    ]

    X = training_data[features]
    y = training_data['champion']

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    return model

if __name__ == "__main__":
    trained_model = model_training()
    print(f"Model created: {trained_model}")