from heartsense.train import build_preprocessor
from heartsense.data import load_raw, clean, split_xy
from sklearn.compose import ColumnTransformer

def test_preprocessor_type():
    pre = build_preprocessor()
    assert isinstance(pre, ColumnTransformer)

def test_preprocessor_shapes():
    df = clean(load_raw())
    X, _ = split_xy(df)
    pre = build_preprocessor()
    Xt = pre.fit_transform(X)
    assert Xt.shape[0] == X.shape[0]
    assert Xt.shape[1] > 0