import datetime
import streamlit as st
import sys
import os
import pandas as pd

# Load races.csv to find the last race date of 2024 (copied from drivers.py)
def get_last_2024_race_date():
    races = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "archive", "races.csv"))
    races_2024 = races[races['year'] == 2024]
    races_2024['date'] = pd.to_datetime(races_2024['date'])
    last_date = races_2024['date'].max().date()
    return last_date

LAST_2024_RACE_DATE = get_last_2024_race_date()
today = datetime.date.today()

# Show filters for team analysis (adapted from drivers.py, without driver comparison)
def show_filters_team():
    with st.expander("Show/Hide Filters", expanded=True):
        # --- Team Comparison Toggle and Options ---
        st.session_state.setdefault("enable_team_comparison", False)
        st.session_state.setdefault("compare_team_name", None)
        st.session_state.setdefault("team_color", "#1f77b4")
        st.session_state.setdefault("compare_team_color", "#ff7f0e")
        enable_comparison = st.checkbox("Enable Team Comparison", value=st.session_state["enable_team_comparison"])
        st.session_state["enable_team_comparison"] = enable_comparison

        # Color pickers for main and comparison team
        st.session_state["team_color"] = st.color_picker("Primary Team Color", st.session_state["team_color"])
        if enable_comparison:
            # Only include teams who raced between 2018-2024
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            DATA_DIR = os.path.join(BASE_DIR, "archive")
            constructors = pd.read_csv(os.path.join(DATA_DIR, "constructors.csv"))
            results = pd.read_csv(os.path.join(DATA_DIR, "results.csv"))
            races = pd.read_csv(os.path.join(DATA_DIR, "races.csv"))
            races_range = races[(races['year'] >= 2018) & (races['year'] <= 2024)]
            race_ids = races_range['raceId'].unique()
            results_range = results[results['raceId'].isin(race_ids)]
            active_team_ids = results_range['constructorId'].unique()
            filtered_teams = constructors[constructors['constructorId'].isin(active_team_ids)]
            team_names = filtered_teams['name'].tolist()
            # Remove the selected team from the comparison list
            selected_team = st.session_state.get("selected_team_name")
            if selected_team in team_names:
                team_names.remove(selected_team)
            st.selectbox("Select Team to Compare", [None] + sorted(team_names), key="compare_team_name")
            st.session_state["compare_team_color"] = st.color_picker("Comparison Team Color", st.session_state["compare_team_color"])

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
                key="team_start_date"
            )
            end_date = st.date_input(
                "End Date",
                value=end_default,
                min_value=start_date,
                max_value=LAST_2024_RACE_DATE,
                key="team_end_date"
            )

            if st.button("Load Data", key="load_custom_timeframe_team"):
                st.session_state["custom_timeframe"] = (start_date, end_date)
                st.session_state["custom_timeframe_selected"] = True
                st.session_state["race_season_selected"] = False

        elif timeframe == "Race Season":
            # Only show seasons the selected team has raced in (2018-2024)
            # This logic should be handled in the main team page, but you can add a placeholder here if needed
            season_options = [2024, 2023, 2022, 2021, 2020, 2019, 2018]
            season_choice = st.selectbox(
                "Select Season:", season_options,
                key="team_season_choice"
            )
            if st.button("Load Data", key="load_race_season_team"):
                st.session_state["race_season"] = season_choice
                st.session_state["race_season_selected"] = True
                st.session_state["custom_timeframe_selected"] = False

def show_team_page(team_name):
    st.subheader(f"Analysis for {team_name}")

    col1, col2 = st.columns(2)
    style = """
    <div style="
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        ">
        <small style="color:gray;">{label}</small><br>
        <span style="font-size:20px;">{value}</span>
    </div>
    """

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "archive")
    constructors = pd.read_csv(os.path.join(DATA_DIR, "constructors.csv"))

    # Find nationality for the team
    nationality = ""
    row = constructors[constructors['name'] == team_name]
    if not row.empty:
        nationality = row.iloc[0]['nationality']
    col1.markdown(style.format(label="Team Name", value=team_name), unsafe_allow_html=True)
    col2.markdown(style.format(label="Nationality", value=nationality), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    show_filters_team()
