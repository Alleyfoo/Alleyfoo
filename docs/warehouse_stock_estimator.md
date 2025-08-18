# Warehouse Stock Estimator

Core functionality from the notebook is available as module `stockforecast`.

## Installation
Create a Python environment and install the required libraries:

```bash
pip install pandas numpy prophet plotly openpyxl kaleido
```

## Data Preparation
1. Mount Google Drive (if using Colab) or set a local data directory.
2. Generate or load historical daily demand for each item. Data should contain:
   - `item_id`: unique identifier
   - `ds`: date column
   - `daily_sales`: units sold per day
3. Use the helper function to simulate stock levels from demand and export the results to Excel for verification.

## Running Forecasts
1. Train a Prophet model on the historical `daily_sales` data.
2. Create a future dataframe and forecast the next 180 days of demand.
3. Accumulate predicted sales to project remaining inventory for each item.
4. Save a dashboard (`forecast_dashboard.xlsx`) and individual item plots to the data directory.

## Interpreting Plots
The notebook plots projected inventory levels with a horizontal reorder threshold.  
When the inventory line crosses this threshold, schedule replenishment before the indicated date.
