"""
Example: run the Lidl receipt processor and analysis,
then save two charts to disk.

Usage:
    python examples/lidl_receipt_demo.py /path/to/receipts_folder /path/to/output.csv
"""

import sys
import os
import pandas as pd

from toolbox.receipt import (
    process_receipts_folder,
    analyze_receipts,
    plot_monthly_spend,
    plot_category_pie,
)


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python examples/lidl_receipt_demo.py <receipts_folder> <csv_output_path>"
        )
        sys.exit(1)

    folder_path = sys.argv[1]
    csv_path = sys.argv[2]

    # 1) Process receipts (OCR + CSV caching)
    df = process_receipts_folder(folder_path, csv_path)

    # 2) If DataFrame is empty, exit
    if df.empty:
        print("No receipt data found; exiting.")
        sys.exit(0)

    # 3) Run analysis computations
    results = analyze_receipts(df)
    monthly_df = results["monthly_spend"]
    top5_df = results["top5_by_month"]
    category_df = results["category_summary_latest"]
    latest_month = results["latest_month"]

    # 4) Print summaries to console
    print("\n=== Monthly Spend ===")
    print(monthly_df.to_string(index=False))
    print("\n=== Top 5 Items by Month ===")
    print(top5_df.to_string(index=False))
    print(f"\n=== Category Spend Breakdown for {latest_month} ===")
    print(category_df.to_string(index=False))

    # 5) Create and save plots
    os.makedirs("examples/figures", exist_ok=True)

    fig1 = plot_monthly_spend(monthly_df)
    fig1_path = os.path.join("examples/figures", "monthly_spend.png")
    fig1.savefig(fig1_path)
    print(f"\nSaved monthly spend chart to: {fig1_path}")

    fig2 = plot_category_pie(category_df, latest_month)
    fig2_path = os.path.join("examples/figures", f"category_pie_{latest_month}.png")
    fig2.savefig(fig2_path)
    print(f"Saved category pie chart to: {fig2_path}")


if __name__ == "__main__":
    main()
