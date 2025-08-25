import streamlit as st
import datetime

today = datetime.date.today()
if "custom_timeframe" not in st.session_state:
    st.session_state["custom_timeframe"] = (datetime.date(2025, 2, 1), today)

if "race_season" not in st.session_state:
    st.session_state["race_season"] = 2025

def show_timeframe_filters():
    timeframe = st.segmented_control("Select a timeframe format", ["Race Season", "Custom Timeframe"])

    if timeframe == "Custom Timeframe":
        start_date = st.date_input(
            "Start Date",
            value=st.session_state["custom_timeframe"][0],
            min_value=datetime.date(2018, 1, 1),
            max_value=today
        )
        end_date = st.date_input(
            "End Date",
            value=st.session_state["custom_timeframe"][1],
            min_value=start_date,
            max_value=today
        )

        st.session_state["custom_timeframe"] = (start_date, end_date)

    elif timeframe == "Race Season":
        season_choice = st.selectbox("Select Season:", [2025, 2024, 2024, 2022, 2021, 2020, 2019, 2018])
        st.session_state["race_season"] = season_choice

def driver_analysis(start_date, end_date):
    pass

def show_driver_page(session, driver_id):
    driver = session.get_driver(driver_id)
    st.subheader(f"Analysis for {driver['FullName']}")

    st.write(f"**Abbreviation:** {driver['Abbreviation']}")
    st.write(f"**Team:** {driver['TeamName']}")

    show_timeframe_filters()
