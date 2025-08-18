"""Utilities for parsing Lidl receipt images into structured data."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any, Callable, Iterable, List, Dict

import click

try:  # pragma: no cover - optional dependency
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore

CATEGORY_MAP = {
    "milk": "Dairy",
    "cheese": "Dairy",
    "yogurt": "Dairy",
    "chicken": "Meat",
    "beef": "Meat",
    "bread": "Bakery",
    "roll": "Bakery",
    "beer": "Drinks",
    "soda": "Drinks",
    "chocolate": "Snacks",
    "chip": "Snacks",
}


def categorize(name: str) -> str:
    """Return a high-level category for a product name.

    Args:
        name: Product name from the receipt.

    Returns:
        Category such as ``"Dairy"`` or ``"Other"``.
    """
    lowered = name.lower()
    for key, category in CATEGORY_MAP.items():
        if key in lowered:
            return category
    return "Other"


def _parse_lines(lines: Iterable[str]) -> List[Dict[str, Any]]:
    """Parse OCR lines into receipt item dictionaries."""
    items: List[Dict[str, Any]] = []
    weight_pattern = re.compile(
        r"^(?P<item>.+?)\s+(?P<weight>\d+(?:\.\d+)?)kg\s+(?P<price>\d+(?:[.,]\d+)?)$"
    )
    qty_pattern = re.compile(
        r"^(?P<item>.+?)\s+(?P<qty>\d+(?:\.\d+)?)\s+(?P<price>\d+(?:[.,]\d+)?)$"
    )
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        weight = qty = None
        m = weight_pattern.match(line)
        if m:
            item = m.group("item")
            weight = float(m.group("weight"))
            price = float(m.group("price").replace(",", "."))
        else:
            m = qty_pattern.match(line)
            if not m:
                continue
            item = m.group("item")
            qty = float(m.group("qty"))
            price = float(m.group("price").replace(",", "."))
        items.append({"item": item, "item_qty": qty, "weight_kg": weight, "price": price})
    return items


def extract_receipt_data(
    path: str | Path, ocr_func: Callable[[Path], str] | None = None
) -> List[Dict[str, Any]]:
    """Extract item dictionaries from a receipt file.

    Args:
        path: Path to an image or text file representing a receipt.
        ocr_func: Optional callable returning OCR text when given the file path.
            If omitted, the file is read as UTF-8 text. This allows passing in a
            stub during tests without requiring OCR dependencies.

    Returns:
        A list of item dictionaries with keys ``item``, ``item_qty``, ``weight_kg``
        and ``price``. Lines that cannot be parsed are skipped.
    """
    file_path = Path(path)
    text = ocr_func(file_path) if ocr_func else file_path.read_text(encoding="utf-8")
    return _parse_lines(text.splitlines())


def process_receipts_folder(
    folder: str | Path,
    csv_out: str | Path | None = None,
    ocr_func: Callable[[Path], str] | None = None,
):
    """Process all receipt files in a folder.

    Args:
        folder: Directory containing receipt images or text files.
        csv_out: Optional path to write the parsed data as CSV.
        ocr_func: Optional callable forwarded to :func:`extract_receipt_data`.

    Returns:
        A :class:`pandas.DataFrame` if pandas is installed, otherwise a list of
        dictionaries.
    """
    folder_path = Path(folder)
    records: List[Dict[str, Any]] = []
    for pattern in ("*.png", "*.jpg", "*.jpeg", "*.txt"):
        for file in folder_path.glob(pattern):
            records.extend(extract_receipt_data(file, ocr_func=ocr_func))
    for rec in records:
        rec["category"] = categorize(rec["item"])
    if csv_out:
        fieldnames = ["item", "item_qty", "weight_kg", "price", "category"]
        with open(csv_out, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
    if pd is not None:  # pragma: no cover - pandas not in test env
        return pd.DataFrame.from_records(records)
    return records


@click.command()
@click.argument("folder", type=click.Path(exists=True, file_okay=False))
@click.argument("csv_out", type=click.Path())
def main(folder: str, csv_out: str) -> None:
    """CLI entry point for processing receipts."""
    process_receipts_folder(folder, csv_out)


__all__ = ["categorize", "extract_receipt_data", "process_receipts_folder", "main"]


if __name__ == "__main__":  # pragma: no cover
    main()
