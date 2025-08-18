from pathlib import Path

import pytest

from lidltracker import categorize, extract_receipt_data, process_receipts_folder


def test_import():
    assert callable(categorize)
    assert callable(extract_receipt_data)
    assert callable(process_receipts_folder)


def test_categorize():
    assert categorize("Fresh milk") == "Dairy"
    assert categorize("Unknown item") == "Other"


def test_process_folder(tmp_path: Path):
    sample = "Milk 1 1.50\nBread 2 2.00\n"
    receipt = tmp_path / "receipt1.txt"
    receipt.write_text(sample, encoding="utf-8")

    data = process_receipts_folder(tmp_path, tmp_path / "out.csv")
    assert any(row["item"] == "Milk" for row in data)
    milk = next(row for row in data if row["item"] == "Milk")
    assert milk["category"] == "Dairy"
    assert (tmp_path / "out.csv").exists()


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        extract_receipt_data(Path("nonexistent.txt"))
