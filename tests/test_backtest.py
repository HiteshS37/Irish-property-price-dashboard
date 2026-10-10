"""Regression tests for baseline forecasts and backtest shape."""
import pandas as pd
import pytest
from scripts.irppi_backtest import SERIES, forecast_baselines, rolling_backtest


def fixture_df(n=60):
    d = {"Date": pd.date_range("2019-01-01", periods=n, freq="MS")}
    for i, col in enumerate(SERIES):
        d[col] = [100 + i * 10 + j for j in range(n)]
    return pd.DataFrame(d)


def test_baselines_and_counts():
    df = fixture_df()
    scores = rolling_backtest(df, horizon=6, min_train=36)
    assert len(scores) == 3 * 3 * (60 - 36 - 6 + 1)
    assert set(scores["method"]) == {"last_value", "seasonal_naive", "trailing_growth"}
    assert scores["absolute_error"].ge(0).all()


def test_future_values_cannot_affect_first_prediction():
    base = fixture_df()
    alternate = base.copy()
    for col in SERIES:
        alternate.loc[42:, col] = 1_000_000
    original = rolling_backtest(base)
    changed = rolling_backtest(alternate)
    first = lambda x: x.loc[x["origin"] == "2021-12-01", ["series", "method", "forecast"]].reset_index(drop=True)
    pd.testing.assert_frame_equal(first(original), first(changed))


def test_invalid_or_missing_index():
    with pytest.raises(ValueError):
        forecast_baselines(pd.Series([100] * 12))
    df = fixture_df()
    df.loc[4, "Date"] = df.loc[3, "Date"]
    with pytest.raises(ValueError):
        rolling_backtest(df)
