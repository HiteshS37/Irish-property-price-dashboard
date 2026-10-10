"""Rolling-origin forecast comparison for the Irish RPPI index series.

This evaluates *indices*, not euro house prices. A test origin must have at
least 13 historical monthly index levels; each evaluation uses only information
available at that origin. Results are descriptive backtests, not causal proof.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

DATA_PATH = Path("data/irppi_national_dublin.csv")
OUT_PATH = Path("data/irppi_backtest_results.csv")
SERIES = [
    "National - all residential properties",
    "Dublin - all residential properties",
    "National excluding Dublin - all residential properties",
]


def forecast_baselines(history: pd.Series, horizon: int = 6) -> dict[str, float]:
    """Return six-month-ahead baseline predictions using history only."""
    if len(history) < 13 or horizon <= 0:
        raise ValueError("At least 13 training observations and a positive horizon required")
    if history.isna().any() or (history <= 0).any():
        raise ValueError("Index series must contain positive, nonmissing values")
    last = float(history.iloc[-1])
    growth = (last / float(history.iloc[-13])) ** (1 / 12) - 1
    return {
        "last_value": last,
        "trailing_growth": last * (1 + growth) ** horizon,
        # Seasonal naive repeats the observation for the same calendar month.
        "seasonal_naive": float(history.iloc[-12 + (horizon - 1) % 12]),
    }


def rolling_backtest(df: pd.DataFrame, horizon: int = 6, min_train: int = 36) -> pd.DataFrame:
    """Evaluate a fixed forecast horizon at expanding-window origins."""
    if horizon < 1 or horizon > 12:
        raise ValueError("horizon must lie between 1 and 12")
    if min_train < 13:
        raise ValueError("min_train must be at least 13")
    df = df.sort_values("Date").reset_index(drop=True)
    if df["Date"].duplicated().any():
        raise ValueError("Duplicate dates found")
    dates = pd.DatetimeIndex(df["Date"])
    expected = pd.date_range(dates.min(), dates.max(), freq="MS")
    if len(dates) != len(expected) or not dates.equals(expected):
        raise ValueError("Dates must be consecutive monthly observations")
    output = []
    for col in SERIES:
        s = pd.to_numeric(df[col], errors="raise")
        for end in range(min_train, len(df) - horizon + 1):
            hist = s.iloc[:end]
            observed = float(s.iloc[end + horizon - 1])
            for method, prediction in forecast_baselines(hist, horizon).items():
                output.append({
                    "series": col,
                    "origin": dates[end - 1].date().isoformat(),
                    "target": dates[end + horizon - 1].date().isoformat(),
                    "horizon_months": horizon,
                    "method": method,
                    "actual": observed,
                    "forecast": prediction,
                    "absolute_error": abs(observed - prediction),
                    "squared_error": (observed - prediction) ** 2,
                })
    return pd.DataFrame(output)


def main() -> None:
    df = pd.read_csv(DATA_PATH, parse_dates=["Date"])
    results = rolling_backtest(df)
    if results.empty:
        raise ValueError("Not enough observations for rolling evaluation")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT_PATH, index=False)
    summary = results.groupby(["series", "method"], as_index=False).agg(
        MAE=("absolute_error", "mean"),
        MSE=("squared_error", "mean"),
        origins=("origin", "nunique"),
    )
    summary["RMSE"] = summary["MSE"].pow(0.5)
    print(summary[["series", "method", "origins", "MAE", "RMSE"]].to_string(index=False))


if __name__ == "__main__":
    main()
