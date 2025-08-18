# Lidl Receipt Analysis

## Objective
This notebook converts scanned Lidl grocery receipts into structured spend summaries. It performs OCR on each image, categorizes items, and produces monthly totals and visualizations.

## Input Format
- Folder containing receipt images (`.png`, `.jpg`, `.jpeg`). Filenames should begin with `YYYY.MM.DD` so the date can be inferred.
- Parsed data are saved to a CSV with columns such as `item`, `price`, `purchase_count`, `item_qty`, `weight_kg`, `date`, and `category`.

## Main Functions
- `categorize(name: str) -> str`: maps product names to categories like Dairy, Meat, Bakery, Drinks, Snacks, or Other.
- `extract_receipt_data(path: str) -> list[dict]`: runs Tesseract OCR on a receipt image, merges continuation lines, captures quantities or weights, and returns item dictionaries.
- `process_receipts_folder(folder: str, csv_out: str) -> pd.DataFrame`: processes all receipt images in a folder, applies `extract_receipt_data`, saves results to CSV, and tags each item with a category.

## Example Output
Running the notebook on sample receipts generates a monthly spend table and category breakdown:

```
Monthly spend
     month  Total Spend
0  2025-05       802.57

Top-5 spend items / month
      month                      item  price
25  2025-05   Ehrmann Maitorahka 0,2%  30.26
20  2025-05  Bellarom Crema kahvipavu  23.50
...

2025-05 – spend by category
  category   price
0    Dairy   77.80
1     Meat   31.61
...
Heaviest 5 items (kg total)
item
Varhaiskaali                4.622
Kurkku Suomi                3.918
...
```
