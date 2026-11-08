"""Feature engineering helpers shared between training and inference."""
import pandas as pd

from heartsense.data import NUMERIC, CATEGORICAL

ALL_FEATURES = NUMERIC + CATEGORICAL

def select_features(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in ALL_FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")
    return df[ALL_FEATURES].copy()

def validate_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """Soft sanity checks (raise on impossible values)."""
    if (df["Age"] < 1).any() or (df["Age"] > 120).any():
        raise ValueError("Age out of physiological range")
    if (df["RestingBP"] < 50).any() or (df["RestingBP"] > 250).any():
        raise ValueError("RestingBP out of physiological range")
    if (df["Cholesterol"] < 0).any() or (df["Cholesterol"] > 700).any():
        raise ValueError("Cholesterol out of range")
    return df