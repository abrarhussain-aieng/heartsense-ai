from pathlib import Path
import pandas as pd
import numpy as np

RAW_PATH = Path("data/raw/heart.csv")
TARGET = "HeartDisease"
NUMERIC = ["Age", "RestingBP", "Cholesterol", "FastingBS", "MaxHR", "Oldpeak"]
CATEGORICAL = ["Sex", "ChestPainType", "RestingECG", "ExerciseAngina", "ST_Slope"]

def load_raw() -> pd.DataFrame:
    return pd.read_csv(RAW_PATH)

def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Biologically impossible zeros → treat as missing
    df.loc[df["RestingBP"] == 0, "RestingBP"] = np.nan
    df.loc[df["Cholesterol"] == 0, "Cholesterol"] = np.nan
    # Negative Oldpeak is physiologically possible; keep it
    return df

def split_xy(df: pd.DataFrame):
    X = df.drop(columns=[TARGET])
    y = df[TARGET].astype(int)
    return X, y