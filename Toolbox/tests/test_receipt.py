import os
import pandas as pd
import tempfile
import pytest

from toolbox.receipt import (
    categorize,
    extract_receipt_data,
    process_receipts_folder,
    analyze_receipts,
    plot_monthly_spend,
    plot_category_pie,
)


def test_categorize_various():
    assert categorize("Täysmaitoa") == "Dairy"
    assert categorize("Kananfilee") == "Meat"
    assert categorize("Vaalealeipä") == "Bakery"
    assert categorize("Kivennäisvesi") == "Drinks"
    assert categorize("Suklaapatukka") == "Snacks"
    assert categorize("JotainMuuta") == "Other"


def test_extract_receipt_data_dummy(tmp_path):
    # Create a fake image with text that matches the regex "item    price"
    # For a real smoke test you might skip OCR altogether and simulate:
    img_path = tmp_path / "2025.06.04_dummy.jpg"
    # Create a tiny white image so Tesseract can run, but its text will be empty
    from PIL import Image

    Image.new("RGB", (100, 30), color="white").save(img_path)
    items = extract_receipt_data(str(img_path))
    # No text detected, so list should be empty
    assert isinstance(items, list)


def test_process_and_analyze(tmp_path):
    # Create a temporary folder for images and CSV
    folder = tmp_path / "receipts"
    folder.mkdir()
    # Write one valid CSV to skip OCR
    csv_path = tmp_path / "data.csv"
    df_dummy = pd.DataFrame(
        {
            "item": ["maito", "liha"],
            "price": [2.50, 5.00],
            "date": ["2025-06-01", "2025-06-02"],
        }
    )
    df_dummy["category"] = df_dummy["item"].apply(categorize)
    df_dummy.to_csv(csv_path, index=False)

    df_loaded = process_receipts_folder(str(folder), str(csv_path))
    # Since csv_path exists, it should load it without errors
    assert df_loaded.shape == (2, 4)  # 4 columns: item, price, date, category
    analysis = analyze_receipts(df_loaded)
    # Check keys exist
    assert "monthly_spend" in analysis
    assert "top5_by_month" in analysis
    assert "category_summary_latest" in analysis

    # All plotting functions should return a Figure
    fig1 = plot_monthly_spend(analysis["monthly_spend"])
    assert hasattr(fig1, "savefig")
    fig2 = plot_category_pie(
        analysis["category_summary_latest"], analysis["latest_month"]
    )
    assert hasattr(fig2, "savefig")
