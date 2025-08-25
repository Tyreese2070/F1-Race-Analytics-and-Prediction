import streamlit as st

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

    import sys
    import os
    import pandas as pd
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
