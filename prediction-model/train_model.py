import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "archive")

races = pd.read_csv(os.path.join(DATA_DIR, "races.csv"))
results = pd.read_csv(os.path.join(DATA_DIR, "results.csv"))
driver_standings = pd.read_csv(os.path.join(DATA_DIR, "driver_standings.csv"))
drivers = pd.read_csv(os.path.join(DATA_DIR, "drivers.csv"))

drivers['full_name'] = drivers['forename'] + ' ' + drivers['surname']

def calculate_features(year, cutoff_race, results_df):
    """Calculates features for all drivers in a given season up to a given cutoff race."""
    pass

def create_training_set():
    """Creates the training set for the model."""
    pass

def model_training():
    """Trains the model on the training set."""
    pass