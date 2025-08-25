import streamlit as st
import datetime

today = datetime.date.today()

# Initialize session state
if "custom_timeframe" not in st.session_state:
    st.session_state["custom_timeframe"] = (datetime.date(2025, 2, 1), today)
if "race_season" not in st.session_state:
    st.session_state["race_season"] = 2025

def show_timeframe_filters():
    timeframe = st.segmented_control(
        "Select a timeframe format", ["Race Season", "Custom Timeframe"]
    )

    if timeframe == "Custom Timeframe":
        start_default, end_default = st.session_state.get("custom_timeframe", (datetime.date(2025,2,1), today))
        start_date = st.date_input(
            "Start Date",
            value=start_default,
            min_value=datetime.date(2018, 1, 1),
            max_value=today,
            key="start_date"
        )
        end_date = st.date_input(
            "End Date",
            value=end_default,
            min_value=start_date,
            max_value=today,
            key="end_date"
        )

        if st.button("Load Data", key="load_custom_timeframe"):
            st.session_state["custom_timeframe"] = (start_date, end_date)
            st.session_state["custom_timeframe_selected"] = True
            st.session_state["race_season_selected"] = False

    elif timeframe == "Race Season":
        season_choice = st.selectbox(
            "Select Season:", [2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018],
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


def show_driver_page(session, driver_id):
    driver = session.get_driver(driver_id)

    # Display info in 3 columns
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
    col1.markdown(style.format(label="Driver Name", value=driver['FullName']), unsafe_allow_html=True)
    col2.markdown(style.format(label="Number", value=driver_id), unsafe_allow_html=True)
    col3.markdown(style.format(label="Team", value=driver['TeamName']), unsafe_allow_html=True)

    # Show timeframe filters
    show_timeframe_filters()

    # Analysis
    driver_analysis()
