import os
import streamlit as st
import driver, team
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "archive")

drivers = pd.read_csv(os.path.join(DATA_DIR, "drivers.csv"), na_values=["\\N"])
constructors = pd.read_csv(os.path.join(DATA_DIR, "constructors.csv"))
races = pd.read_csv(os.path.join(DATA_DIR, "races.csv"))
results = pd.read_csv(os.path.join(DATA_DIR, "results.csv"))

def get_recent_driver_constructors():
    '''
    Get all drivers and their most recent constructor information
    '''

    # Get all races between 2018 and 2024
    races_range = races[(races['year'] >= 2018) & (races['year'] <= 2024)]
    race_ids = races_range['raceId'].unique()

    results_range = results[results['raceId'].isin(race_ids)]

    df = results_range.merge(drivers, on='driverId', how='left') \
                     .merge(constructors, on='constructorId', how='left')
    
    # Get the last team for each driver in this range
    df = df.sort_values(["driverId", "raceId"]).drop_duplicates("driverId", keep="last")

    # Map driver names to their most recent team information
    mapping = {}
    for _, row in df.iterrows():
        full_name = f"{row['forename']} {row['surname']}"
        driver_number = row.get("number_x")
        if pd.isna(driver_number):
            driver_number = row.get("number_y")
        mapping[full_name] = {
            "driverId": row["driverId"],
            "TeamName": row["name"],
            "DriverNumber": driver_number,
            "forename": row.get("forename", ""),
            "surname": row.get("surname", "")
        }
    return mapping

def get_teams():
    '''
    Get all teams and their information
    '''
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
    driver_list = [None] + sorted(mapping.keys())
    selected_driver = st.selectbox("Select a driver:", driver_list, format_func=lambda x: x if x else "None")

    st.session_state["selected_driver_name"] = selected_driver
    if selected_driver:
        driver.show_driver_page(mapping[selected_driver])

elif option == "Team Analysis":
    # Get all teams that have raced between 2018-2024
    races_range = races[(races['year'] >= 2018) & (races['year'] <= 2024)]
    race_ids = races_range['raceId'].unique()
    results_range = results[results['raceId'].isin(race_ids)]
    team_ids = results_range['constructorId'].unique()
    teams_in_range = constructors[constructors['constructorId'].isin(team_ids)]
    team_names = [None] + sorted(teams_in_range['name'].unique())
    selected_team = st.selectbox("Select a team:", team_names, format_func=lambda x: x if x else "None")
    if selected_team:
        team.show_team_page(selected_team)