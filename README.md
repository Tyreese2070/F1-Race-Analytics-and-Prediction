# Notes
- Pit stop times from the data contains the time for the entire pit sequence from pitlane entry to pitlane exit, not just the time to change tyres and release the car.

# Initial Setup
```
pip install requirements.txt
```

# Running instructions
```
cd /pages
streamlit run app.py
```
# Data Source
https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020/data

# 2025 World Champion Prediction Model
## Features
- Currrent points in WDC
- Avg points / race
- Wins
- Podiums
- Avg Finishing position
- Team performance ??
- Head to head vs teammates or WDC contender

## Model
- Random Forest Classifier?

## Data
- Use kaggle data with 2025 season.
- Create, find, or web scrape the 2025 season data. Could ask chatgpt to generate a csv of results for all drivers this season to add to the data