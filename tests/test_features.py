import pandas as pd
from heartsense.features import select_features, ALL_FEATURES

def test_select_features():
    df = pd.DataFrame({c: [1] for c in ALL_FEATURES})
    out = select_features(df)
    assert list(out.columns) == ALL_FEATURES