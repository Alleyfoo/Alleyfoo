# Warehouse Stock Estimator

Utilities for simulating demand and forecasting when to reorder stock using [Prophet](https://facebook.github.io/prophet/).

## Installation

```bash
pip install -r requirements.txt
```

## Quick start

```python
from warehousestock.estimator import generate_daily_demand, forecast_reorder_date

demand = generate_daily_demand("2024-01-01", "2024-01-30", base_sales_mean=20, item_id="ITEM_1")
reorder_date = forecast_reorder_date(demand, current_stock=500, reorder_threshold=100)
print(reorder_date)
```

## Functions
- `generate_daily_demand` – create a demand DataFrame with seasonality and noise.
- `simulate_stock_from_demand` – simulate stock levels and replenishments.
- `forecast_reorder_date` – predict when inventory will fall below a threshold.
