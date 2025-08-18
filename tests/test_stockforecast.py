import pytest

pd = pytest.importorskip("pandas")

from stockforecast import (
    ForecastResult,
    forecast_inventory,
    generate_daily_demand,
    simulate_stock_from_demand,
)


def test_import():
    assert callable(generate_daily_demand)
    assert callable(simulate_stock_from_demand)
    assert callable(forecast_inventory)


def test_simulation():
    df = generate_daily_demand("2024-01-01", "2024-01-10", 10, "A")
    result = simulate_stock_from_demand(df, 60, 4, 14, 7)
    assert "stock" in result.columns
    assert len(result) == len(df)


def test_forecast_with_stub():
    df = pd.DataFrame(
        {
            "ds": pd.date_range("2024-01-01", periods=5, freq="D"),
            "daily_sales": [1, 1, 1, 1, 1],
        }
    )

    class DummyProphet:
        def fit(self, df: pd.DataFrame) -> None:
            self.last_date = df["ds"].max()

        def make_future_dataframe(self, periods: int) -> pd.DataFrame:
            return pd.DataFrame(
                {
                    "ds": pd.date_range(
                        self.last_date + pd.Timedelta(days=1), periods=periods, freq="D"
                    )
                }
            )

        def predict(self, future: pd.DataFrame) -> pd.DataFrame:
            return pd.DataFrame({"ds": future["ds"], "yhat": [1.0] * len(future)})

    result = forecast_inventory(
        df,
        current_inventory=3,
        forecast_days=5,
        reorder_threshold=1,
        prophet_cls=DummyProphet,
    )
    assert isinstance(result, ForecastResult)
    assert result.reorder_date is not None


def test_missing_column():
    with pytest.raises(ValueError):
        simulate_stock_from_demand(pd.DataFrame({"ds": []}), 60, 4, 14, 7)
