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
            season_options = [2024, 2023, 2022, 2021, 2020, 2019, 2018]
            season_choice = st.selectbox(
                "Select Season:", season_options,
                key="team_season_choice"
            )
            if st.button("Load Data", key="load_race_season_team"):
                st.session_state["race_season"] = season_choice
                st.session_state["race_season_selected"] = True
                st.session_state["custom_timeframe_selected"] = False

def team_points_analysis():
    import plotly.express as px
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "archive")
    results = pd.read_csv(os.path.join(DATA_DIR, "results.csv"))
    races = pd.read_csv(os.path.join(DATA_DIR, "races.csv"))
    constructors = pd.read_csv(os.path.join(DATA_DIR, "constructors.csv"))
    try:
        sprint_results = pd.read_csv(os.path.join(DATA_DIR, "sprint_results.csv"))
    except Exception:
        sprint_results = pd.DataFrame(columns=results.columns)

    # Get selected teams from session state
    selected_team = st.session_state.get("selected_team_name")
    compare_team = st.session_state.get("compare_team_name") if st.session_state.get("enable_team_comparison") else None
    team_colors = {
        selected_team: st.session_state.get("team_color", "#1f77b4"),
    }
    if compare_team:
        team_colors[compare_team] = st.session_state.get("compare_team_color", "#ff7f0e")

    #  list of teams to plot
    teams_to_plot = [selected_team]
    if compare_team:
        teams_to_plot.append(compare_team)

    # Timeframe 
    if st.session_state.get("custom_timeframe_selected", False):
        start_date, end_date = st.session_state["custom_timeframe"]
        races["date"] = pd.to_datetime(races["date"])
        races_in_timeframe = races[(races["date"] >= pd.to_datetime(start_date)) & (races["date"] <= pd.to_datetime(end_date))]
    else:
        season = st.session_state.get("race_season", 2024)
        races_in_timeframe = races[races["year"] == season]
    race_ids = races_in_timeframe["raceId"].unique()

    import plotly.graph_objects as go
    stats = []
    fig = go.Figure()
    # Ensure all teams use the same x-axis 
    x_dates = races_in_timeframe["date"]
    for team_name in teams_to_plot:
        if not team_name:
            continue
        team_row = constructors[constructors['name'] == team_name]
        if team_row.empty:
            merged = races_in_timeframe[["raceId", "date", "name", "year"]].copy()
            merged["points"] = 0
            merged["accum_points"] = 0
        else:
            team_id = team_row.iloc[0]['constructorId']
            try:
                team_id = int(team_id)
            except Exception:
                pass
            team_results = results[(results["constructorId"].astype(int) == team_id) & (results["raceId"].isin(race_ids))]
            team_sprint_results = sprint_results[(sprint_results["constructorId"].astype(int) == team_id) & (sprint_results["raceId"].isin(race_ids))]
            common_cols = [col for col in team_results.columns if col in team_sprint_results.columns]
            all_results = pd.concat([team_results[common_cols], team_sprint_results[common_cols]], ignore_index=True)
            grouped = all_results.groupby("raceId", as_index=False).agg({
                "points": "sum",
                "positionOrder": "min"  # best finish for the team in each race
            })
            merged = races_in_timeframe[["raceId", "date", "name", "year"]].merge(grouped, on="raceId", how="left")
            merged = merged.sort_values("date")
            merged["points"] = merged["points"].fillna(0)
            merged["accum_points"] = merged["points"].cumsum()
            merged["positionOrder"] = merged["positionOrder"].replace(0, pd.NA)
        fig.add_scatter(
            x=merged["date"],
            y=merged["accum_points"],
            mode="lines+markers",
            name=team_name,
            line=dict(color=team_colors[team_name])
        )

        # Get best finish
        if "positionOrder" in merged.columns and merged["positionOrder"].notna().any():
            best_finish = int(merged["positionOrder"].min())
        else:
            best_finish = None
        stats.append({
            "label": team_name,
            "total_points": merged["points"].sum(),
            "avg_points": merged["points"].mean(),
            "best_finish": best_finish
        })
    if len(stats) > 0:
        fig.update_layout(
            xaxis=dict(tickformat="%Y-%m-%d"),
            title="Accumulated Team Points Over Time",
            xaxis_title="Race Date",
            yaxis_title="Accumulated Points"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Show stats for each team, with delta if comparison enabled
        if len(stats) == 2:
            s1, s2 = stats[0], stats[1]
            col1, col2, col3 = st.columns(3)
            def percent_delta(a, b):
                if b == 0:
                    return None
                if a == b:
                    return "="
                return f"{round((a-b)/b*100, 1)}%"
            # Total Points
            delta1 = percent_delta(s1["total_points"], s2["total_points"])
            delta2 = percent_delta(s2["total_points"], s1["total_points"])
            col1.metric(f"Total Points ({s1['label']})", s1["total_points"], delta=delta1)
            col1.metric(f"Total Points ({s2['label']})", s2["total_points"], delta=delta2)
            # Best Finish
            best1 = s1['best_finish'] if s1['best_finish'] is not None else 0
            best2 = s2['best_finish'] if s2['best_finish'] is not None else 0
            def best_delta(a, b):
                if a == 0 or b == 0:
                    return None
                if a == b:
                    return "="
                diff = b - a
                sign = "+" if diff > 0 else ""
                return f"{sign}{diff}"
            col2.metric(f"Best Finish ({s1['label']})", f"P{best1}" if best1 else "-", delta=best_delta(best1, best2))
            col2.metric(f"Best Finish ({s2['label']})", f"P{best2}" if best2 else "-", delta=best_delta(best2, best1))
            # Avg Points
            avg1 = round(s1["avg_points"], 2)
            avg2 = round(s2["avg_points"], 2)
            avg_delta1 = percent_delta(avg1, avg2)
            avg_delta2 = percent_delta(avg2, avg1)
            col3.metric(f"Avg Points per race ({s1['label']})", avg1, delta=avg_delta1)
            col3.metric(f"Avg Points per race ({s2['label']})", avg2, delta=avg_delta2)
        else:
            for s in stats:
                col1, col2, col3 = st.columns(3)
                col1.metric(f"Total Points ({s['label']})", s["total_points"])
                best = s['best_finish'] if s['best_finish'] is not None else 0
                col2.metric(f"Best Finish ({s['label']})", f"P{best}" if best else "-")
                avg = round(s["avg_points"], 2)
                col3.metric(f"Avg Points per race ({s['label']})", avg)
    else:
        st.info("No team points data for the selected team(s) in the selected timeframe.")

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
    team_points_analysis()
