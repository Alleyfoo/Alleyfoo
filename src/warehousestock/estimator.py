"""Forecast inventory levels and reorder dates using Prophet."""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

try:  # pragma: no cover - optional dependency
    from prophet import Prophet
except Exception:  # pragma: no cover
    Prophet = None  # type: ignore[assignment]


def generate_daily_demand(
    start_date: str | pd.Timestamp,
    end_date: str | pd.Timestamp,
    base_sales_mean: float,
    item_id: str,
) -> pd.DataFrame:
    """Simulate daily demand for a single item.

    Args:
        start_date: First date of the simulation.
        end_date: Last date of the simulation.
        base_sales_mean: Average daily sales for the item.
        item_id: Identifier for the item.

    Returns:
        DataFrame with columns ``item_id``, ``ds`` and ``daily_sales``.
    """
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    df = pd.DataFrame({"ds": dates})
    noise = np.random.normal(0, base_sales_mean * 0.1, len(df))
    df["daily_sales"] = base_sales_mean + noise
    df["daily_sales"] += np.sin(df["ds"].dt.dayofyear / 365 * 2 * np.pi) * (base_sales_mean * 0.2)
    df["daily_sales"] += np.sin(df["ds"].dt.dayofweek / 7 * 2 * np.pi) * (base_sales_mean * 0.1)
    df["daily_sales"] = df["daily_sales"].apply(lambda x: max(1, round(x)))
    df["item_id"] = item_id
    return df[["item_id", "ds", "daily_sales"]]


def simulate_stock_from_demand(
    df_demand_history: pd.DataFrame,
    initial_stock_multiplier: int,
    replenishment_order_size_weeks: int,
    lead_time_days: int,
    safety_stock_days: int,
) -> pd.DataFrame:
    """Simulate stock levels for historical demand data.

    Args:
        df_demand_history: Demand history with columns ``ds`` and ``daily_sales``.
        initial_stock_multiplier: Days of average sales kept as initial stock.
        replenishment_order_size_weeks: Order size expressed in weeks of demand.
        lead_time_days: Supplier lead time in days.
        safety_stock_days: Safety stock expressed in days of demand.

    Returns:
        DataFrame with an added ``stock`` column representing inventory levels.
    """
    df = df_demand_history.sort_values("ds").copy()
    avg_daily_sales = df["daily_sales"].mean()
    initial_stock = int(avg_daily_sales * initial_stock_multiplier)
    current_stock = initial_stock

    replenishment_threshold = int(avg_daily_sales * (lead_time_days + safety_stock_days))
    replenishment_amount = int(avg_daily_sales * (replenishment_order_size_weeks * 7))
    df["stock"] = 0

    for i, row in df.iterrows():
        df.at[i, "stock"] = current_stock
        current_stock -= row["daily_sales"]
        if current_stock < replenishment_threshold and i < len(df) - lead_time_days:
            current_stock += replenishment_amount
    return df


def forecast_reorder_date(
    item_data: pd.DataFrame,
    current_stock: int,
    reorder_threshold: int,
    periods: int = 180,
) -> Optional[pd.Timestamp]:
    """Forecast when inventory will fall below a threshold.

    Args:
        item_data: DataFrame with columns ``ds`` and ``daily_sales``.
        current_stock: Current inventory level.
        reorder_threshold: Stock level triggering a reorder.
        periods: Days to forecast into the future.

    Returns:
        Date when projected stock drops below ``reorder_threshold``.
        Returns ``None`` if the threshold is not crossed within ``periods`` days.
    """
    if Prophet is None:  # pragma: no cover - executed only when Prophet missing
        raise ImportError(
            "prophet is required for forecasting. Install it via 'pip install prophet'."
        )

    prophet_df = item_data[["ds", "daily_sales"]].rename(columns={"daily_sales": "y"})
    model = Prophet()
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    forecast = forecast[forecast["ds"] > prophet_df["ds"].max()].copy()
    forecast["cumulative_sales"] = forecast["yhat"].cumsum()
    forecast["projected_stock"] = current_stock - forecast["cumulative_sales"]
    below = forecast[forecast["projected_stock"] <= reorder_threshold]
    if below.empty:
        return None
    return pd.to_datetime(below.iloc[0]["ds"])
