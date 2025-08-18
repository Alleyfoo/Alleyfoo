import warehousestock
from warehousestock.estimator import (
    forecast_reorder_date,
    generate_daily_demand,
)


def test_import():
    assert hasattr(warehousestock, "forecast_reorder_date")


def test_forecast_reorder_date():
    demand = generate_daily_demand("2024-01-01", "2024-01-10", base_sales_mean=10, item_id="SKU1")
    date = forecast_reorder_date(demand, current_stock=50, reorder_threshold=5, periods=30)
    assert date is not None


def test_no_reorder_needed():
    demand = generate_daily_demand("2024-01-01", "2024-01-10", base_sales_mean=1, item_id="SKU1")
    date = forecast_reorder_date(demand, current_stock=1000, reorder_threshold=10, periods=30)
    assert date is None
