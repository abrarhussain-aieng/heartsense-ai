import pandas as pd
from heartsense.data import clean, load_raw, split_xy

def test_no_zero_after_clean():
    df = clean(load_raw())
    assert (df["RestingBP"].dropna() > 0).all()
    assert (df["Cholesterol"].dropna() > 0).all()

def test_split_shapes():
    df = clean(load_raw())
    X, y = split_xy(df)
    assert len(X) == len(y)
    assert "HeartDisease" not in X.columns
    assert y.isin([0, 1]).all()