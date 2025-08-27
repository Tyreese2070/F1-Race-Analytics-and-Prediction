import streamlit as st
import datetime
import pandas as pd
import plotly.express as px

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

def show_filters():
    with st.expander("Show/Hide Filters", expanded=True):
        timeframe = st.segmented_control(
            "Select a timeframe format", ["Race Season", "Custom Timeframe"]
        )

        # Driver comparison toggle and options
        st.session_state.setdefault("enable_comparison", False)
        st.session_state.setdefault("compare_driver_name", None)
        st.session_state.setdefault("driver_color", "#1f77b4")
        st.session_state.setdefault("compare_driver_color", "#ff7f0e")
        enable_comparison = st.checkbox("Enable Driver Comparison", value=st.session_state["enable_comparison"])
        st.session_state["enable_comparison"] = enable_comparison

        # Color pickers for main and comparison driver
        st.session_state["driver_color"] = st.color_picker("Primary Driver Color", st.session_state["driver_color"])
        if enable_comparison:
            # Only include drivers who raced between 2018-2024
            drivers_df = pd.read_csv("../archive/drivers.csv")
            results_df = pd.read_csv("../archive/results.csv")
            races_df = pd.read_csv("../archive/races.csv")
            races_range = races_df[(races_df['year'] >= 2018) & (races_df['year'] <= 2024)]
            race_ids = races_range['raceId'].unique()
            results_range = results_df[results_df['raceId'].isin(race_ids)]
            active_driver_ids = results_range['driverId'].unique()
            filtered_drivers = drivers_df[drivers_df['driverId'].isin(active_driver_ids)]
            driver_names = (filtered_drivers['forename'] + ' ' + filtered_drivers['surname']).tolist()

            # Remove the selected driver from the comparison list
            selected_driver = st.session_state.get("selected_driver_name")
            if selected_driver in driver_names:
                driver_names.remove(selected_driver)
            st.selectbox("Select Driver to Compare", [None] + driver_names, key="compare_driver_name")
            st.session_state["compare_driver_color"] = st.color_picker("Comparison Driver Color", st.session_state["compare_driver_color"])

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
            # Only show seasons the selected driver has raced in (2018-2024)
            selected_driver = st.session_state.get("selected_driver_name")
            seasons = []
            if selected_driver:
                # Load results and races
                results = pd.read_csv("../archive/results.csv")
                races = pd.read_csv("../archive/races.csv")
                drivers = pd.read_csv("../archive/drivers.csv")
                # Find driverId for selected_driver
                forename, surname = selected_driver.split(" ", 1)
                driver_row = drivers[(drivers['forename'] == forename) & (drivers['surname'] == surname)]
                if not driver_row.empty:
                    driver_id = driver_row.iloc[0]['driverId']
                    driver_results = results[results['driverId'] == driver_id]
                    merged = driver_results.merge(races, on='raceId', how='left')
                    years = merged[(merged['year'] >= 2018) & (merged['year'] <= 2024)]['year'].unique()
                    seasons = sorted(years, reverse=True)
            if not seasons:
                seasons = [2024, 2023, 2022, 2021, 2020, 2019, 2018]
            season_choice = st.selectbox(
                "Select Season:", seasons,
                key="season_choice"
            )
            if st.button("Load Data", key="load_race_season"):
                st.session_state["race_season"] = season_choice
                st.session_state["race_season_selected"] = True
                st.session_state["custom_timeframe_selected"] = False

def points_analysis(driver):
    '''
    Graphs to represent driver points performance
    '''

    # State the current timeframe the user chose
    if st.session_state.get("custom_timeframe_selected", False):
        start_date, end_date = st.session_state["custom_timeframe"]
        st.write(f"**Analysis from {start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}**")
    else:
        season = st.session_state.get("race_season", 2024)
        st.write(f"**Analysis for the {season} season**")

    # Prepare drivers to plot: list of dicts {driver, color}
    drivers_to_plot = []
    drivers_to_plot.append({"driver": driver, "color": st.session_state.get("driver_color", "#1f77b4")})
    if st.session_state.get("enable_comparison") and st.session_state.get("compare_driver_name"):
        compare_name = st.session_state["compare_driver_name"]
        if compare_name:
            # Load driver info
            drivers_df = pd.read_csv("../archive/drivers.csv")
            forename, surname = compare_name.split(" ", 1)
            row = drivers_df[(drivers_df['forename'] == forename) & (drivers_df['surname'] == surname)]
            if not row.empty:
                compare_driver = row.iloc[0].to_dict()
                drivers_to_plot.append({"driver": compare_driver, "color": st.session_state.get("compare_driver_color", "#ff7f0e")})

    # Load results, sprint results, and races
    results = pd.read_csv("../archive/results.csv")
    try:
        sprint_results = pd.read_csv("../archive/sprint_results.csv")
    except Exception:
        sprint_results = pd.DataFrame(columns=results.columns)
    races = pd.read_csv("../archive/races.csv")

    # Filter by timeframe
    if st.session_state.get("custom_timeframe_selected", False):
        start_date, end_date = st.session_state["custom_timeframe"]
        races["date"] = pd.to_datetime(races["date"])
        races_in_timeframe = races[(races["date"] >= pd.to_datetime(start_date)) & (races["date"] <= pd.to_datetime(end_date))]
    else:
        season = st.session_state.get("race_season", 2024)
        races_in_timeframe = races[races["year"] == season]

    race_ids = races_in_timeframe["raceId"].unique()

    # Plot all drivers
    fig = None
    stats = []
    for d in drivers_to_plot:
        drv = d["driver"]
        color = d["color"]
        driver_id = drv.get("driverId")
        # Filter both results and sprint_results for this driver and races in timeframe
        driver_results = results[(results["driverId"] == driver_id) & (results["raceId"].isin(race_ids))]
        driver_sprint_results = sprint_results[(sprint_results["driverId"] == driver_id) & (sprint_results["raceId"].isin(race_ids))]
        # Use only columns that exist in both (for concat)
        common_cols = [col for col in driver_results.columns if col in driver_sprint_results.columns]
        all_results = pd.concat([driver_results[common_cols], driver_sprint_results[common_cols]], ignore_index=True)
        # Group by raceId and sum points (to include both main race and sprint points)
        grouped = all_results.groupby("raceId", as_index=False).agg({
            "points": "sum",
            "positionOrder": "min"  # best finish in any session for that raceId
        })
        # Merge with race info for date, name, year
        merged = grouped.merge(races[["raceId", "date", "name", "year"]], on="raceId", how="left")
        merged = merged.sort_values("date")
        merged["accum_points"] = merged["points"].cumsum()
        label = f"{drv.get('forename', '')} {drv.get('surname', '')}".strip()
        if not merged.empty:
            if fig is None:
                fig = px.line(
                    merged,
                    x="date",
                    y="accum_points",
                    markers=True,
                    labels={"date": "Race Date", "accum_points": "Accumulated Points"},
                    title="Accumulated Points Over Time"
                )
                fig.update_traces(mode="lines+markers", selector=0, line_color=color, name=label)
            else:
                fig.add_scatter(
                    x=merged["date"],
                    y=merged["accum_points"],
                    mode="lines+markers",
                    name=label,
                    line=dict(color=color)
                )
            stats.append({
                "label": label,
                "total_points": merged["points"].sum(),
                "best_finish": merged["positionOrder"].min(),
                "avg_points": merged["points"].mean()
            })
        else:
            stats.append({
                "label": label,
                "total_points": 0,
                "best_finish": None,
                "avg_points": 0
            })
    if fig:
        fig.update_layout(xaxis=dict(tickformat="%Y-%m-%d"))
        st.plotly_chart(fig, use_container_width=True)
        # Show stats for each driver, with delta if comparison enabled
        if len(stats) == 2:
            s1, s2 = stats[0], stats[1]
            col1, col2, col3 = st.columns(3)
            # Total Points Percentage Delta
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

            # Best Finish (lower is better, so invert delta, but show as %)
            best1 = s1['best_finish'] if s1['best_finish'] is not None else 0
            best2 = s2['best_finish'] if s2['best_finish'] is not None else 0
            def best_percent_delta(a, b):
                if a == 0 or b == 0:
                    return None
                if a == b:
                    return "="
                return f"{round((b-a)/a*100, 1)}%"  # lower is better

            col2.metric(f"Best Finish ({s1['label']})", f"P{best1}" if best1 else "-")
            col2.metric(f"Best Finish ({s2['label']})", f"P{best2}" if best2 else "-")

            # Avg Points Percentage Delta, rounded to 2dp
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
                col2.metric(f"Best Finish ({s['label']})", f"P{s['best_finish']}" if s['best_finish'] is not None else "-")
                col3.metric(f"Avg Points ({s['label']})", round(s["avg_points"], 2))
    else:
        st.info("No race data for the selected driver(s) in the selected timeframe.")


def qualifying_analysis(driver):
    '''
    Graphs to represent driver qualifying performance
    '''

    # State the current timeframe the user chose
    if st.session_state.get("custom_timeframe_selected", False):
        start_date, end_date = st.session_state["custom_timeframe"]
        st.write(f"**Qualifying Analysis from {start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}**")
    else:
        season = st.session_state.get("race_season", 2024)
        st.write(f"**Qualifying Analysis for the {season} season**")

    # Prepare drivers to plot: list of dicts {driver, color}
    drivers_to_plot = []
    drivers_to_plot.append({"driver": driver, "color": st.session_state.get("driver_color", "#1f77b4")})
    if st.session_state.get("enable_comparison") and st.session_state.get("compare_driver_name"):
        compare_name = st.session_state["compare_driver_name"]
        if compare_name:
            # Load driver info
            drivers_df = pd.read_csv("../archive/drivers.csv")
            forename, surname = compare_name.split(" ", 1)
            row = drivers_df[(drivers_df['forename'] == forename) & (drivers_df['surname'] == surname)]
            if not row.empty:
                compare_driver = row.iloc[0].to_dict()
                drivers_to_plot.append({"driver": compare_driver, "color": st.session_state.get("compare_driver_color", "#ff7f0e")})

    # Load qualifying and races data
    qualifying = pd.read_csv("../archive/qualifying.csv")
    races = pd.read_csv("../archive/races.csv")

    # Filter by timeframe
    if st.session_state.get("custom_timeframe_selected", False):
        start_date, end_date = st.session_state["custom_timeframe"]
        races["date"] = pd.to_datetime(races["date"])
        races_in_timeframe = races[(races["date"] >= pd.to_datetime(start_date)) & (races["date"] <= pd.to_datetime(end_date))]
    else:
        season = st.session_state.get("race_season", 2024)
        races_in_timeframe = races[races["year"] == season]

    race_ids = races_in_timeframe["raceId"].unique()

    fig = None
    stats = []
    for d in drivers_to_plot:
        drv = d["driver"]
        color = d["color"]
        driver_id = drv.get("driverId")
        driver_qualifying = qualifying[(qualifying["driverId"] == driver_id) & (qualifying["raceId"].isin(race_ids))]
        merged = driver_qualifying.merge(races[["raceId", "date", "name", "year"]], on="raceId", how="left")
        merged = merged.sort_values("date")
        label = f"{drv.get('forename', '')} {drv.get('surname', '')}".strip()

        if not merged.empty:
            if fig is None:
                fig = px.line(
                    merged,
                    x="date",
                    y="position",
                    markers=True,
                    labels={"date": "Race Date", "position": "Qualifying Position"},
                    title="Qualifying Position Over Time"
                )
                fig.update_traces(mode="lines+markers", selector=0, line_color=color, name=label)
            else:
                fig.add_scatter(
                    x=merged["date"],
                    y=merged["position"],
                    mode="lines+markers",
                    name=label,
                    line=dict(color=color)
                )

            # Calculate stats
            best_qualifying = merged["position"].min()
            avg_qualifying = merged["position"].mean()
            pole_positions = (merged["position"] == 1).sum()

            stats.append({
                "label": label,
                "best_qualifying": best_qualifying,
                "avg_qualifying": avg_qualifying,
                "pole_positions": pole_positions
            })
        else:
            stats.append({
                "label": label,
                "best_qualifying": None,
                "avg_qualifying": None,
                "pole_positions": 0
            })

    if fig:
        # Reverse y-axis so P1 is at the top
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(xaxis=dict(tickformat="%Y-%m-%d"))
        st.plotly_chart(fig, use_container_width=True)

        # Show stats for each driver, with delta if comparison enabled
        if len(stats) == 2:
            s1, s2 = stats[0], stats[1]
            col1, col2, col3 = st.columns(3)

            def percent_delta(a, b):
                if b == 0: return None
                if a == b: return "="
                return f"{round((a-b)/b*100, 1)}%"

            # Best Qualifying (inverted delta)
            best1 = s1['best_qualifying'] if s1['best_qualifying'] is not None else 0
            best2 = s2['best_qualifying'] if s2['best_qualifying'] is not None else 0
            best_delta1 = None
            if best1 > 0 and best2 > 0:
                best_delta1 = f"{round((best2-best1)/best1*100, 1)}%"
            best_delta2 = None
            if best1 > 0 and best2 > 0:
                best_delta2 = f"{round((best1-best2)/best2*100, 1)}%"

            col1.metric(f"Best Qualifying ({s1['label']})", f"P{best1}" if best1 > 0 else "-", delta=best_delta1)
            col1.metric(f"Best Qualifying ({s2['label']})", f"P{best2}" if best2 > 0 else "-", delta=best_delta2)

            # Avg Qualifying (inverted delta)
            avg1 = round(s1["avg_qualifying"], 2) if s1["avg_qualifying"] is not None else 0
            avg2 = round(s2["avg_qualifying"], 2) if s2["avg_qualifying"] is not None else 0
            avg_delta1 = None
            if avg1 > 0 and avg2 > 0:
                avg_delta1 = f"{round((avg2-avg1)/avg1*100, 1)}%"
            avg_delta2 = None
            if avg1 > 0 and avg2 > 0:
                avg_delta2 = f"{round((avg1-avg2)/avg2*100, 1)}%"

            col2.metric(f"Avg Qualifying ({s1['label']})", avg1, delta=avg_delta1)
            col2.metric(f"Avg Qualifying ({s2['label']})", avg2, delta=avg_delta2)

            # Pole Positions 
            delta_poles = int(s1['pole_positions']) - int(s2['pole_positions'])
            delta_poles_val = str(delta_poles) if delta_poles == 0 else int(delta_poles)
            col3.metric(f"Pole Positions ({s1['label']})", s1['pole_positions'], delta=delta_poles_val)
            delta_poles_rev = int(s2['pole_positions']) - int(s1['pole_positions'])
            delta_poles_rev_val = str(delta_poles_rev) if delta_poles_rev == 0 else int(delta_poles_rev)
            col3.metric(f"Pole Positions ({s2['label']})", s2['pole_positions'], delta=delta_poles_rev_val)
        else:
            for s in stats:
                col1, col2, col3 = st.columns(3)
                col1.metric(f"Best Qualifying ({s['label']})", f"P{s['best_qualifying']}" if s['best_qualifying'] is not None else "-")
                col2.metric(f"Avg Qualifying ({s['label']})", round(s["avg_qualifying"], 2) if s["avg_qualifying"] is not None else "-")
                col3.metric(f"Pole Positions ({s['label']})", s["pole_positions"])
    else:
        st.info("No qualifying data for the selected driver(s) in the selected timeframe.")


def finishing_positions_analysis(driver):
    '''
    Bar chart showing the frequency of finishing positions
    '''
    # State the current timeframe
    if st.session_state.get("custom_timeframe_selected", False):
        start_date, end_date = st.session_state["custom_timeframe"]
        st.write(f"**Finishing Positions from {start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}**")
    else:
        season = st.session_state.get("race_season", 2024)
        st.write(f"**Finishing Positions for the {season} season**")

    # Prepare drivers to plot
    drivers_to_plot = []
    drivers_to_plot.append({"driver": driver, "color": st.session_state.get("driver_color", "#1f77b4")})
    if st.session_state.get("enable_comparison") and st.session_state.get("compare_driver_name"):
        compare_name = st.session_state["compare_driver_name"]
        if compare_name:
            drivers_df = pd.read_csv("../archive/drivers.csv")
            forename, surname = compare_name.split(" ", 1)
            row = drivers_df[(drivers_df['forename'] == forename) & (drivers_df['surname'] == surname)]
            if not row.empty:
                compare_driver = row.iloc[0].to_dict()
                drivers_to_plot.append({"driver": compare_driver, "color": st.session_state.get("compare_driver_color", "#ff7f0e")})

    # Load results and races
    results = pd.read_csv("../archive/results.csv")
    races = pd.read_csv("../archive/races.csv")

    # Filter by timeframe
    if st.session_state.get("custom_timeframe_selected", False):
        start_date, end_date = st.session_state["custom_timeframe"]
        races["date"] = pd.to_datetime(races["date"])
        races_in_timeframe = races[(races["date"] >= pd.to_datetime(start_date)) & (races["date"] <= pd.to_datetime(end_date))]
    else:
        season = st.session_state.get("race_season", 2024)
        races_in_timeframe = races[races["year"] == season]

    race_ids = races_in_timeframe["raceId"].unique()
    all_data = []

    for d in drivers_to_plot:
        drv = d["driver"]
        color = d["color"]
        driver_id = drv.get("driverId")
        driver_name = f"{drv.get('forename', '')} {drv.get('surname', '')}".strip()
        driver_results = results[(results["driverId"] == driver_id) & (results["raceId"].isin(race_ids))]
        if not driver_results.empty:
            counts = driver_results["positionOrder"].value_counts().sort_index().reset_index()
            counts.columns = ["positionOrder", "count"]
            counts["driver"] = driver_name
            counts["color"] = color
            all_data.append(counts)

    if all_data:
        plot_df = pd.concat(all_data)
        # Determine unique positions for consistent bars across drivers
        all_positions = sorted(plot_df["positionOrder"].unique())
        # Use driver name string as key in color_discrete_map
        color_discrete_map = {f"{d['driver'].get('forename', '')} {d['driver'].get('surname', '')}".strip(): d['color'] for d in drivers_to_plot}
        fig = px.bar(
            plot_df,
            x="positionOrder",
            y="count",
            color="driver",
            barmode="group",
            labels={"positionOrder": "Finishing Position", "count": "Number of Finishes"},
            title="Frequency of Finishing Positions",
            color_discrete_map=color_discrete_map,
            category_orders={"positionOrder": all_positions}
        )
        fig.update_layout(xaxis={"categoryorder":"category ascending"})
        st.plotly_chart(fig, use_container_width=True)

        # --- Average Finishing Position Widget(s) ---
        avg_stats = []
        for d in drivers_to_plot:
            drv = d["driver"]
            driver_id = drv.get("driverId")
            driver_name = f"{drv.get('forename', '')} {drv.get('surname', '')}".strip()
            driver_results = results[(results["driverId"] == driver_id) & (results["raceId"].isin(race_ids))]
            # Only count classified finishes (positionOrder > 0)
            classified = driver_results[driver_results["positionOrder"] > 0]
            avg_finish = classified["positionOrder"].mean() if not classified.empty else None
            avg_stats.append({"label": driver_name, "avg_finish": avg_finish})

        if len(avg_stats) == 2:
            s1, s2 = avg_stats[0], avg_stats[1]
            col1, col2 = st.columns(2)
            delta1 = delta2 = None
            if s1["avg_finish"] is not None and s2["avg_finish"] is not None and s2["avg_finish"] != 0 and s1["avg_finish"] != 0:
                percent1 = (s2["avg_finish"] - s1["avg_finish"]) / s2["avg_finish"] * 100
                percent2 = (s1["avg_finish"] - s2["avg_finish"]) / s1["avg_finish"] * 100
                if abs(percent1) < 1e-6:
                    delta1 = delta2 = "="
                else:
                    delta1 = f"{percent1:+.1f}%"
                    delta2 = f"{percent2:+.1f}%"
            col1.metric(f"Avg Finishing Position ({s1['label']})", f"{s1['avg_finish']:.2f}" if s1['avg_finish'] is not None else "-", delta=delta1)
            col2.metric(f"Avg Finishing Position ({s2['label']})", f"{s2['avg_finish']:.2f}" if s2['avg_finish'] is not None else "-", delta=delta2)
        else:
            for s in avg_stats:
                st.metric(f"Avg Finishing Position ({s['label']})", f"{s['avg_finish']:.2f}" if s['avg_finish'] is not None else "-")
    else:
        st.info("No finishing data for the selected driver(s) in the selected timeframe.")

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

    st.markdown("<br>", unsafe_allow_html=True)
    show_filters()

    # Analysis
    points_analysis(driver)
    qualifying_analysis(driver)
    finishing_positions_analysis(driver)
