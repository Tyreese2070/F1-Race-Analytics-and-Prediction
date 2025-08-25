import streamlit as st
import datetime
import pandas as pd

# Load races.csv to find the last race date of 2024
def get_last_2024_race_date():
    races = pd.read_csv("../archive/races.csv")
    races_2024 = races[races['year'] == 2024]
    races_2024['date'] = pd.to_datetime(races_2024['date'])
    last_date = races_2024['date'].max().date()
    return last_date

LAST_2024_RACE_DATE = get_last_2024_race_date()
today = datetime.date.today()

# Initialize session state
if "custom_timeframe" not in st.session_state:
    st.session_state["custom_timeframe"] = (datetime.date(2024, 2, 1), today)
if "race_season" not in st.session_state:
    st.session_state["race_season"] = 2024

def show_timeframe_filters():
    timeframe = st.segmented_control(
        "Select a timeframe format", ["Race Season", "Custom Timeframe"]
    )

    if timeframe == "Custom Timeframe":
        start_default, end_default = st.session_state.get("custom_timeframe", (datetime.date(2024,2,1), LAST_2024_RACE_DATE))
        if start_default < datetime.date(2018, 1, 1):
            start_default = datetime.date(2018, 1, 1)
        if end_default > LAST_2024_RACE_DATE:
            end_default = LAST_2024_RACE_DATE
        if end_default < start_default:
            end_default = start_default

        start_date = st.date_input(
            "Start Date",
            value=start_default,
            min_value=datetime.date(2018, 1, 1),
            max_value=LAST_2024_RACE_DATE,
            key="start_date"
        )
        end_date = st.date_input(
            "End Date",
            value=end_default,
            min_value=start_date,
            max_value=LAST_2024_RACE_DATE,
            key="end_date"
        )

        if st.button("Load Data", key="load_custom_timeframe"):
            st.session_state["custom_timeframe"] = (start_date, end_date)
            st.session_state["custom_timeframe_selected"] = True
            st.session_state["race_season_selected"] = False

    elif timeframe == "Race Season":
        season_choice = st.selectbox(
            "Select Season:", [2024, 2023, 2022, 2021, 2020, 2019, 2018],
            key="season_choice"
        )
        if st.button("Load Data", key="load_race_season"):
            st.session_state["race_season"] = season_choice
            st.session_state["race_season_selected"] = True
            st.session_state["custom_timeframe_selected"] = False

def driver_analysis():
    if st.session_state.get("custom_timeframe_selected", False):
        start_date, end_date = st.session_state["custom_timeframe"]
        st.write(f"**Analysis from {start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}**")
    else:
        season = st.session_state.get("race_season", 2025)
        st.write(f"**Analysis for the {season} season**")

def show_driver_page(driver):
    col1, col2, col3 = st.columns(3)
    style = """
    <div style="
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        ">
        <small style="color:gray;">{label}</small><br>
        <span style="font-size:24px;">{value}</span>
    </div>
    """

    driver_name = f"{driver.get('forename', '')} {driver.get('surname', '')}".strip()
    col1.markdown(style.format(label="Driver Name", value=driver_name), unsafe_allow_html=True)
    col2.markdown(style.format(label="Number", value=driver['DriverNumber']), unsafe_allow_html=True)
    col3.markdown(style.format(label="Team", value=driver['TeamName']), unsafe_allow_html=True)

    # Show timeframe filters
    show_timeframe_filters()

    # Analysis
    driver_analysis()
