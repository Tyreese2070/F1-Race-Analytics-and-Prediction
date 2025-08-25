import fastf1
import os
import streamlit as st
import datetime
import driver, team

# Enable cache
if not os.path.isdir('cache'):
    os.mkdir('cache')
fastf1.Cache.enable_cache('cache')

# Load 2025 schedule
schedule = fastf1.get_event_schedule(2025)

# Get today's date
today = datetime.date.today()

# Get most recent race details
past_races = schedule[schedule['EventDate'].dt.date < today]

if len(past_races) == 0:
    selected_race = schedule.iloc[0]
else:
    selected_race = past_races.iloc[-1]

# Load that session
@st.cache_data(show_spinner=False)
def load_session(year, race_name, session_type):
    session = fastf1.get_session(year, race_name, session_type)
    session.load()
    return session

session = load_session(2025, selected_race['EventName'], 'R')

# Extract drivers
drivers = session.drivers
driver_names = [session.get_driver(d)['FullName'] for d in drivers]

# Get teams
teams = set()
for d in drivers:
    teams.add(session.get_driver(d)['TeamName'])
team_names = list(teams)

# Streamlit UI
st.title("F1 Race Analytics and Prediction")
st.write("Welcome to the F1 Race Analytics and Prediction app!")

st.sidebar.title("Driver or Team Select")
option = st.sidebar.selectbox("Choose an option:", ["Driver Analysis", "Team Analysis"])

if option == "Driver Analysis":
    driver_map = {session.get_driver(d)['FullName']: d for d in session.drivers}
    selected_driver_name = st.selectbox("Select a driver:", list(driver_map.keys()))
    if selected_driver_name:
        driver_id = driver_map[selected_driver_name]
        driver.show_driver_page(session, driver_id)

elif option == "Team Analysis":
    selected_team = st.selectbox("Select a team:", team_names)
    if selected_team:
        team.show_team_page(selected_team)