"""Weekly category-demand forecasting for Module 3.4.

Compares a 52-week seasonal-naive baseline with additive Holt-Winters.
The final 12 observed weeks are held out for time-based evaluation.

Usage:
    python -m analytics.supply_chain.demand_forecasting
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from analytics.snowflake_utils import query_df


OUTPUT_DIR = Path("analytics/supply_chain")
TOP_CATEGORY_COUNT = 5
TEST_WEEKS = 12
FORECAST_WEEKS = 12
SEASONAL_PERIODS = 52


def make_weekly_series(data: pd.DataFrame, category: str) -> pd.Series:
    """Create a complete Monday-based series, filling absent weeks with zero."""
    category_data = data[data["CATEGORY_NAME"] == category]
    series = category_data.groupby("DEMAND_WEEK")["UNITS_SOLD"].sum().sort_index()
    series.index = pd.to_datetime(series.index)
    full_index = pd.date_range(series.index.min(), series.index.max(), freq="W-MON")
    return series.reindex(full_index, fill_value=0).astype(float)


def seasonal_naive(train: pd.Series, horizon: int) -> pd.Series:
    """Repeat observations from the corresponding weeks one year earlier."""
    if len(train) < SEASONAL_PERIODS:
        raise ValueError("Seasonal naive requires at least 52 weeks.")
    values = np.resize(train.iloc[-SEASONAL_PERIODS:].to_numpy(), horizon)
    index = pd.date_range(
        train.index[-1] + pd.Timedelta(weeks=1), periods=horizon, freq="W-MON"
    )
    return pd.Series(values, index=index)


def holt_winters(train: pd.Series, horizon: int) -> pd.Series:
    """Fit additive Holt-Winters and return non-negative forecasts."""
    if len(train) < 2 * SEASONAL_PERIODS:
        raise ValueError("Holt-Winters requires at least two seasonal cycles.")
    model = ExponentialSmoothing(
        train,
        trend="add",
        seasonal="add",
        seasonal_periods=SEASONAL_PERIODS,
        initialization_method="estimated",
    ).fit(optimized=True)
    return model.forecast(horizon).clip(lower=0)


def mae(actual: pd.Series, predicted: pd.Series) -> float:
    """Mean absolute error measured in units."""
    return float(np.mean(np.abs(actual.to_numpy() - predicted.to_numpy())))


def wape(actual: pd.Series, predicted: pd.Series) -> float:
    """Weighted absolute percentage error; lower is better."""
    denominator = float(np.abs(actual.to_numpy()).sum())
    if denominator == 0:
        return float("nan")
    error = np.abs(actual.to_numpy() - predicted.to_numpy()).sum()
    return float(error / denominator)


def main() -> None:
    weekly = query_df(
        "SELECT demand_week, category_name, units_sold FROM vw_demand_weekly"
    )
    weekly["DEMAND_WEEK"] = pd.to_datetime(weekly["DEMAND_WEEK"])
    weekly["UNITS_SOLD"] = pd.to_numeric(weekly["UNITS_SOLD"])

    category_totals = (
        weekly.groupby("CATEGORY_NAME")["UNITS_SOLD"].sum().sort_values(ascending=False)
    )
    top_categories = category_totals.head(TOP_CATEGORY_COUNT).index.tolist()
    metrics: list[dict[str, object]] = []
    future_forecasts: list[pd.DataFrame] = []

    for category in top_categories:
        series = make_weekly_series(weekly, category)
        train = series.iloc[:-TEST_WEEKS]
        test = series.iloc[-TEST_WEEKS:]
        predictions = {
            "seasonal_naive": seasonal_naive(train, TEST_WEEKS),
            "holt_winters": holt_winters(train, TEST_WEEKS),
        }

        for model_name, prediction in predictions.items():
            prediction.index = test.index
            metrics.append(
                {
                    "category": category,
                    "model": model_name,
                    "mae_units": mae(test, prediction),
                    "wape": wape(test, prediction),
                }
            )

        category_metrics = [row for row in metrics if row["category"] == category]
        winner = min(category_metrics, key=lambda row: row["wape"])["model"]
        future = (
            seasonal_naive(series, FORECAST_WEEKS)
            if winner == "seasonal_naive"
            else holt_winters(series, FORECAST_WEEKS)
        )
        future_forecasts.append(
            pd.DataFrame(
                {
                    "forecast_week": future.index,
                    "category_name": category,
                    "forecast_units": future.to_numpy(),
                    "selected_model": winner,
                }
            )
        )

        plt.figure(figsize=(12, 5))
        history = series.iloc[-64:]
        plt.plot(history.index, history.values, label="Actual")
        plt.plot(future.index, future.values, "--", label=f"Forecast: {winner}")
        plt.axvline(series.index[-1], color="gray", linestyle=":")
        plt.title(f"12-week demand forecast: {category}")
        plt.xlabel("Week")
        plt.ylabel("Units sold")
        plt.legend()
        plt.tight_layout()
        safe_name = "".join(
            char.lower() if char.isalnum() else "_" for char in category
        ).strip("_")
        plt.savefig(OUTPUT_DIR / f"forecast_{safe_name}.png")
        plt.close()

    metrics_df = pd.DataFrame(metrics).sort_values(["category", "wape"])
    forecasts_df = pd.concat(future_forecasts, ignore_index=True)

    print("Backtest metrics (lower is better):")
    printable = metrics_df.copy()
    printable["wape"] = printable["wape"].map(lambda value: f"{value:.1%}")
    print(printable.to_string(index=False))

    print("\nSelected model by category:")
    winners = metrics_df.loc[
        metrics_df.groupby("category")["wape"].idxmin(),
        ["category", "model", "mae_units", "wape"],
    ]
    print(winners.to_string(index=False))

    metrics_path = OUTPUT_DIR / "forecast_backtest_metrics.csv"
    forecasts_path = OUTPUT_DIR / "category_demand_forecasts.csv"
    metrics_df.to_csv(metrics_path, index=False)
    forecasts_df.to_csv(forecasts_path, index=False)
    print(f"\nSaved metrics to {metrics_path}")
    print(f"Saved forecasts to {forecasts_path}")
    print("Saved one forecast chart per category.")
    print(
        "\nCaution: a sharp volume shift near late 2017 makes this a modeling "
        "demonstration, not production inventory guidance."
    )


if __name__ == "__main__":
    main()
