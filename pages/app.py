import os
import streamlit as st
import datetime
import driver, team
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "archive")

drivers = pd.read_csv(os.path.join(DATA_DIR, "drivers.csv"), na_values=["\\N"])
constructors = pd.read_csv(os.path.join(DATA_DIR, "constructors.csv"))
races = pd.read_csv(os.path.join(DATA_DIR, "races.csv"))
results = pd.read_csv(os.path.join(DATA_DIR, "results.csv"))

def get_recent_driver_constructors(year=None):
    if year is None:
        year = races['year'].max()
    
    races_year = races[races['year'] == year]
    race_ids = races_year['raceId'].unique()

    results_year = results[results['raceId'].isin(race_ids)]

    df = results_year.merge(drivers, on='driverId', how='left') \
                     .merge(constructors, on='constructorId', how='left')
    
    df = df.sort_values(["driverId", "raceId"]).drop_duplicates("driverId", keep="last")

    mapping = {}
    for _, row in df.iterrows():
        full_name = f"{row['forename']} {row['surname']}"
        driver_number = row.get("number_x")
        if pd.isna(driver_number):
            driver_number = row.get("number_y")
        mapping[full_name] = {
            "TeamName": row["name"],
            "DriverNumber": driver_number,
            "forename": row.get("forename", ""),
            "surname": row.get("surname", "")
        }
    return mapping

def get_teams():
    teams_info = {}
    for _, row in constructors.iterrows():
        teams_info[row['name']] = {
            "TeamName": row['name'],
            "Nationality": row['nationality'],
            "ConstructorRef": row['constructorRef'],
            "ConstructorId": row['constructorId']
        }
    return teams_info


# Streamlit UI
st.title("F1 Race Analytics and Prediction")
st.write("Welcome to the F1 Race Analytics and Prediction app!")
st.button("Info")

st.sidebar.title("Driver or Team Select")
option = st.sidebar.selectbox("Choose an option:", ["Driver Analysis", "Team Analysis"])

mapping = get_recent_driver_constructors()

if option == "Driver Analysis":
    selected_driver = st.selectbox("Select a driver:", list(mapping.keys()))
    if selected_driver:
        driver.show_driver_page(mapping[selected_driver])

elif option == "Team Analysis":
    team_names = sorted({v['TeamName'] for v in mapping.values() if v.get('TeamName')})
    selected_team = st.selectbox("Select a team:", team_names)
    if selected_team:
        team.show_team_page(selected_team)