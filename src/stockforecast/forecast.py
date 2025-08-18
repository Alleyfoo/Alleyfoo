"""Forecast inventory depletion using simple demand simulation and Prophet."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional, Type

import click

try:  # pragma: no cover - optional dependency
    import pandas as pd  # type: ignore
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore
    np = None  # type: ignore


@dataclass
class ForecastResult:
    """Container for forecast output."""

    forecast: "pd.DataFrame"
    reorder_date: Optional[date]


def generate_daily_demand(
    start_date: str | date,
    end_date: str | date,
    base_sales_mean: int,
    item_id: str,
) -> "pd.DataFrame":
    """Generate simulated daily demand for an item.

    Args:
        start_date: Beginning of the simulation period.
        end_date: End of the simulation period.
        base_sales_mean: Average daily sales used as the distribution mean.
        item_id: Identifier for the item.

    Returns:
        DataFrame with columns ``item_id``, ``ds`` (date) and ``daily_sales``.
    """
    if pd is None or np is None:  # pragma: no cover - dependency missing
        raise ImportError("pandas and numpy are required for demand generation")

    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    df = pd.DataFrame({"ds": dates})
    noise = np.random.normal(0, base_sales_mean * 0.1, len(df))
    df["daily_sales"] = base_sales_mean + noise
    df["daily_sales"] = df["daily_sales"].apply(lambda x: max(1, round(x)))
    df["item_id"] = item_id
    return df[["item_id", "ds", "daily_sales"]]


def simulate_stock_from_demand(
    df_demand_history: "pd.DataFrame",
    initial_stock_multiplier: int,
    replenishment_order_size_weeks: int,
    lead_time_days: int,
    safety_stock_days: int,
) -> "pd.DataFrame":
    """Simulate stock levels given historical demand.

    Args:
        df_demand_history: DataFrame with columns ``ds`` and ``daily_sales``.
        initial_stock_multiplier: Multiplier for average daily sales to set initial stock.
        replenishment_order_size_weeks: Size of replenishment orders measured in weeks of demand.
        lead_time_days: Supplier lead time in days.
        safety_stock_days: Additional days of stock to keep as safety.

    Returns:
        Copy of input ``df_demand_history`` with an added ``stock`` column.

    Raises:
        ValueError: If ``daily_sales`` column is missing.
    """
    if pd is None:  # pragma: no cover
        raise ImportError("pandas is required for stock simulation")
    if "daily_sales" not in df_demand_history.columns:
        raise ValueError("df_demand_history must contain 'daily_sales' column")

    df = df_demand_history.sort_values("ds").copy()
    avg_daily_sales = df["daily_sales"].mean()
    initial_stock = int(avg_daily_sales * initial_stock_multiplier)
    current_stock = initial_stock
    threshold = int(avg_daily_sales * (lead_time_days + safety_stock_days))
    replenishment = int(avg_daily_sales * (replenishment_order_size_weeks * 7))
    df["stock"] = 0
    for i, row in df.iterrows():
        df.loc[i, "stock"] = current_stock
        current_stock -= row["daily_sales"]
        if current_stock < threshold and i < len(df) - lead_time_days:
            current_stock += replenishment
    return df


def forecast_inventory(
    df_demand_history: "pd.DataFrame",
    current_inventory: int,
    forecast_days: int,
    reorder_threshold: int,
    prophet_cls: Optional[Type] = None,
) -> ForecastResult:
    """Forecast inventory depletion using Prophet.

    Args:
        df_demand_history: Historical demand with columns ``ds`` and ``daily_sales``.
        current_inventory: Current stock level.
        forecast_days: Number of days to forecast into the future.
        reorder_threshold: Inventory level triggering replenishment.
        prophet_cls: Optional ``prophet.Prophet`` class for dependency injection in tests.

    Returns:
        :class:`ForecastResult` with forecast dataframe and the date when inventory
        falls below ``reorder_threshold`` (or ``None`` if not within range).
    """
    if pd is None:  # pragma: no cover
        raise ImportError("pandas is required for forecasting")

    if prophet_cls is None:
        try:  # pragma: no cover - heavy dependency
            from prophet import Prophet as prophet_cls  # type: ignore
        except Exception as e:  # pragma: no cover
            raise ImportError("prophet is required for forecasting") from e

    hist = df_demand_history.rename(columns={"daily_sales": "y"})[["ds", "y"]]
    model = prophet_cls()
    model.fit(hist)
    future = model.make_future_dataframe(periods=forecast_days)
    forecast = model.predict(future)[["ds", "yhat"]]
    future_sales = forecast[forecast["ds"] > hist["ds"].max()].copy()
    future_sales["cumulative_sales"] = future_sales["yhat"].cumsum()
    future_sales["projected_inventory"] = current_inventory - future_sales["cumulative_sales"]
    below = future_sales[future_sales["projected_inventory"] < reorder_threshold]
    reorder_date = below["ds"].iloc[0].date() if not below.empty else None
    return ForecastResult(future_sales, reorder_date)


@click.command()
@click.argument("csv_path", type=click.Path(exists=True))
@click.argument("current_inventory", type=int)
@click.argument("reorder_threshold", type=int)
@click.option("--forecast-days", default=180, show_default=True, type=int)
def main(csv_path: str, current_inventory: int, reorder_threshold: int, forecast_days: int) -> None:
    """CLI entry point for inventory forecasting.

    CSV_PATH should contain columns ``ds`` (date) and ``daily_sales``.
    """
    if pd is None:  # pragma: no cover
        raise ImportError("pandas is required for CLI usage")
    df = pd.read_csv(csv_path, parse_dates=["ds"])
    result = forecast_inventory(df, current_inventory, forecast_days, reorder_threshold)
    if result.reorder_date:
        click.echo(
            f"Inventory will fall below {reorder_threshold} on {result.reorder_date:%Y-%m-%d}"
        )
    else:
        click.echo("Inventory stays above threshold in the forecast horizon")


if __name__ == "__main__":  # pragma: no cover
    main()
