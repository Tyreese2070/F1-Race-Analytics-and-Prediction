import streamlit as st
import pandas as pd
import os
from sklearn.ensemble import RandomForestClassifier

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")
DATA_2025_DIR = os.path.join(BASE_DIR, "F1_2025_Dataset")

# load archive data
results = pd.read_csv(os.path.join(ARCHIVE_DIR, "results.csv"))
try:
    sprint_results = pd.read_csv(os.path.join(ARCHIVE_DIR, "sprint_results.csv"))
except Exception:
    sprint_results = pd.DataFrame(columns=results.columns)
races = pd.read_csv(os.path.join(ARCHIVE_DIR, "races.csv"))
drivers = pd.read_csv(os.path.join(ARCHIVE_DIR, "drivers.csv"))

# feature engineering for data
def get_season_features(year):
    race_ids = races[races['year'] == year]['raceId'].unique()
    season_results = results[results['raceId'].isin(race_ids)]
    season_sprint = sprint_results[sprint_results['raceId'].isin(race_ids)] if not sprint_results.empty else pd.DataFrame(columns=results.columns)
    all_results = pd.concat([season_results, season_sprint], ignore_index=True)
    all_results['positionOrder'] = pd.to_numeric(all_results['positionOrder'], errors='coerce')
    all_results['points'] = pd.to_numeric(all_results['points'], errors='coerce').fillna(0)
    features = all_results.groupby('driverId').agg(
        total_points=('points', 'sum'),
        total_wins=('positionOrder', lambda x: (x == 1).sum()),
        total_podiums=('positionOrder', lambda x: (x <= 3).sum()),
        avg_finishing_position=('positionOrder', 'mean'),
        total_races=('raceId', 'nunique')
    ).reset_index()
    features['avg_points'] = features['total_points'] / features['total_races']
    features['season'] = year
    return features

# training data set
train_years = sorted(races['year'].unique())
train_years = [y for y in train_years if y < 2025]
train_df = pd.concat([get_season_features(y) for y in train_years], ignore_index=True)

def get_champion_driver(year):
    race_ids = races[races['year'] == year]['raceId'].unique()
    season_results = results[results['raceId'].isin(race_ids)]
    season_sprint = sprint_results[sprint_results['raceId'].isin(race_ids)] if not sprint_results.empty else pd.DataFrame(columns=results.columns)
    all_results = pd.concat([season_results, season_sprint], ignore_index=True)
    all_results['points'] = pd.to_numeric(all_results['points'], errors='coerce').fillna(0)
    points_by_driver = all_results.groupby('driverId')['points'].sum()
    if points_by_driver.empty:
        return None
    return points_by_driver.idxmax()

train_df['is_champion'] = train_df.apply(lambda row: int(row['driverId'] == get_champion_driver(row['season'])), axis=1)

# features
model_features = ['total_points','total_wins','total_podiums','avg_finishing_position','total_races','avg_points']
X = train_df[model_features]
y = train_df['is_champion']

# train model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X, y)

# prepare 2025 data
race_results_2025 = pd.read_csv(os.path.join(DATA_2025_DIR, "Formula1_2025Season_RaceResults.csv"))
sprint_results_2025 = pd.read_csv(os.path.join(DATA_2025_DIR, "Formula1_2025Season_SprintResults.csv"))

def get_2025_features(race_results, sprint_results):
    all_results = pd.concat([race_results, sprint_results], ignore_index=True)
    all_results['Position'] = all_results['Position'].replace('NC', None).replace('DQ', None)
    all_results['positionOrder'] = pd.to_numeric(all_results['Position'], errors='coerce')
    all_results['points'] = pd.to_numeric(all_results['Points'], errors='coerce').fillna(0)
    features = all_results.groupby('No').agg(
        total_points=('points', 'sum'),
        total_wins=('positionOrder', lambda x: (x == 1).sum()),
        total_podiums=('positionOrder', lambda x: (x <= 3).sum()),
        avg_finishing_position=('positionOrder', 'mean'),
        total_races=('Track', 'nunique')
    ).reset_index()
    features['avg_points'] = features['total_points'] / features['total_races']
    return features

features_2025 = get_2025_features(race_results_2025, sprint_results_2025)
X_2025 = features_2025[model_features]
probs = clf.predict_proba(X_2025)
champion_idx = probs[:,1].argmax()
champion_row = features_2025.iloc[champion_idx]
champion_no = champion_row['No']

# Get driver name from number
drivers_2025 = race_results_2025[['No','Driver']].drop_duplicates().set_index('No')
champion_name = drivers_2025.loc[champion_no]['Driver'] if champion_no in drivers_2025.index else str(champion_no)

st.title("2025 World Champion Prediction")
st.markdown(f"### Predicted 2025 World Champion: **{champion_name}**")

# Show top 5 probabilities
features_2025['prob_champion'] = probs[:,1]
top5 = features_2025.sort_values('prob_champion', ascending=False).head(5)
top5 = top5.merge(drivers_2025, left_on='No', right_index=True, how='left')
st.markdown("#### Top 5 Probabilities:")
st.dataframe(top5[['Driver','prob_champion','total_points','total_wins','total_podiums','avg_finishing_position','total_races']].set_index('Driver'))