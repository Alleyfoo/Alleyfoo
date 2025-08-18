"""Extract tabular data from a PDF page using OCR."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple
import re

try:  # pragma: no cover - optional dependency
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore

ROW_RE = re.compile(
    r"""^(?P<raw>[-FT]?P[A-Z0-9]{3,})\s+
        (?P<desc>.*?)\s+
        \|?\s*(?P<stat>\d+\s*kg)\s+
        (?P<dyn>\d+\s*kg)\s*$""",
    re.I | re.X | re.M,
)

OCR_MAP = str.maketrans(
    {
        "O": "0",
        "o": "0",
        "S": "5",
        "s": "5",
        "I": "1",
        "l": "1",
        "B": "8",
        "-": "T",
        "F": "T",
        "f": "T",
    }
)


def parse_ocr_text_to_df(text: str) -> "pd.DataFrame":
    """Parse OCR'd table text into a DataFrame.

    Args:
        text: Raw text produced by OCR.

    Returns:
        DataFrame with columns ``Part nr.``, ``Description``, ``Max static load``,
        and ``Max dynamic load``. Empty if no rows were parsed.
    """

    if pd is None:  # pragma: no cover - import guard
        raise ImportError("pandas is required for parse_ocr_text_to_df")

    lines = [ln for ln in text.splitlines() if ln.strip()]
    lines = [ln for ln in lines if not re.search(r"\bPart\s+nr", ln, re.I)]
    cleaned = "\n".join(lines)

    rows = []
    for match in ROW_RE.finditer(cleaned):
        part_norm = match.group("raw").translate(OCR_MAP)
        if re.fullmatch(r"TP\d{3,}", part_norm):
            rows.append(
                {
                    "Part nr.": part_norm,
                    "Description": match.group("desc").strip(),
                    "Max static load": match.group("stat"),
                    "Max dynamic load": match.group("dyn"),
                }
            )

    return pd.DataFrame(rows)


def extract_pdf_table(
    pdf_path: str | Path,
    page_num: int,
    crop_box: Tuple[float, float, float, float],
    dpi: int = 300,
    ocr_lang: str = "eng",
) -> "pd.DataFrame":
    """Extract a table region from a PDF via OCR.

    This function requires ``pymupdf``, ``pytesseract``, and ``Pillow``. These are
    optional and are only imported when the function is called.

    Args:
        pdf_path: Path to the PDF file.
        page_num: 1-based page number to process.
        crop_box: Bounding box ``(x0, y0, x1, y1)`` specifying the table region.
        dpi: Rasterization resolution for OCR.
        ocr_lang: Tesseract language code.

    Returns:
        DataFrame parsed from the OCR text.
    """

    if pd is None:  # pragma: no cover
        raise ImportError("pandas is required for extract_pdf_table")

    try:  # pragma: no cover - optional dependency
        import fitz  # type: ignore
        from PIL import Image  # type: ignore
        import pytesseract  # type: ignore
        import io
    except Exception as exc:  # pragma: no cover
        raise ImportError(
            "pymupdf, pillow, and pytesseract must be installed to extract tables"
        ) from exc

    page = fitz.open(pdf_path).load_page(page_num - 1)
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), clip=fitz.Rect(*crop_box))
    img = Image.open(io.BytesIO(pix.tobytes()))
    ocr_text = pytesseract.image_to_string(img, lang=ocr_lang)
    return parse_ocr_text_to_df(ocr_text)


def save_table_to_excel(
    df: "pd.DataFrame",
    out_path: str | Path,
    sheet_name: str = "Sheet1",
) -> None:
    """Save a DataFrame to an Excel file.

    Args:
        df: DataFrame returned from :func:`extract_pdf_table` or
            :func:`parse_ocr_text_to_df`.
        out_path: Destination ``.xlsx`` file.
        sheet_name: Name of the sheet to create.
    """

    df.to_excel(out_path, sheet_name=sheet_name, index=False)
