import fastf1
import os
import streamlit as st
import datetime

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
session = fastf1.get_session(2025, selected_race['EventName'], 'R')
session.load()

# Extract drivers
drivers = session.drivers
driver_names = [session.get_driver(d)['FullName'] for d in drivers]

# Streamlit UI
st.title("F1 Race Analytics and Prediction")
st.write("Welcome to the F1 Race Analytics and Prediction app!")

st.sidebar.title("Driver or Team Select")
option = st.sidebar.selectbox("Choose an option:", ["Driver Analysis", "Team Analysis"])

if option == "Driver Analysis":
    driver = st.selectbox("Select a driver:", driver_names)
elif option == "Team Analysis":
    # placeholder names (add dynamic teams loading later)
    team = st.selectbox("Select a team:", ["Red Bull", "Ferrari", "Mercedes", "McLaren", "Williams", "Aston Martin", "Alpine", "Racing Bulls", "Haas", "Sauber", "Cadillac"])
