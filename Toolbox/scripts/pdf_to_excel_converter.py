"""Convert a PDF table into an Excel spreadsheet using OCR."""

import io
import re
import fitz
import pytesseract
import pandas as pd
from PIL import Image


def extract_table(pdf_path: str, page_num: int = 1, crop_box: tuple | None = None, dpi: int = 300, lang: str = "eng") -> pd.DataFrame:
    """Extract table rows from a PDF page using OCR.

    Parameters
    ----------
    pdf_path: str
        Path to the input PDF file.
    page_num: int
        1-based page number to process.
    crop_box: tuple | None
        Optional bounding box (x0, y0, x1, y1) to crop before OCR.
    dpi: int
        Rasterization resolution.
    lang: str
        Language for Tesseract OCR.
    """
    page = fitz.open(pdf_path).load_page(page_num - 1)
    rect = fitz.Rect(*crop_box) if crop_box else page.rect
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), clip=rect)
    img = Image.open(io.BytesIO(pix.tobytes()))
    ocr = pytesseract.image_to_string(img, lang=lang)
    ocr_lines = [ln for ln in ocr.splitlines() if ln.strip()]
    ocr_lines = [ln for ln in ocr_lines if not re.search(r"\bPart\s+nr", ln, re.I)]
    clean_ocr = "\n".join(ocr_lines)
    row_re = re.compile(
        r"""^(?P<raw>[-FT]?P[A-Z0-9]{3,})\s+
            (?P<desc>.*?)\s+
            \|?\s*(?P<stat>\d+\s*kg)\s+
            (?P<dyn>\d+\s*kg)\s*$""",
        re.I | re.X | re.M,
    )
    ocr_map = str.maketrans({
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
    })
    rows: list[dict[str, str]] = []
    for m in row_re.finditer(clean_ocr):
        part_norm = m.group("raw").translate(ocr_map)
        if re.fullmatch(r"TP\d{3,}", part_norm):
            rows.append(
                {
                    "Part nr.": part_norm,
                    "Description": m.group("desc").strip(),
                    "Max static load": m.group("stat"),
                    "Max dynamic load": m.group("dyn"),
                }
            )
    return pd.DataFrame(rows)


def export_to_excel(df: pd.DataFrame, out_path: str, sheet_name: str = "Jockey Wheels") -> None:
    """Save a DataFrame to an Excel file."""
    with pd.ExcelWriter(out_path, engine="openpyxl") as xl:
        df.to_excel(xl, sheet_name=sheet_name, index=False)


def main() -> None:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert a PDF table to an Excel spreadsheet using OCR."
    )
    parser.add_argument("input_pdf", help="Path to the input PDF file")
    parser.add_argument("output_xlsx", help="Path to the output XLSX file")
    parser.add_argument("--page", type=int, default=1, help="1-based page number")
    parser.add_argument("--lang", default="eng", help="Tesseract language code")
    args = parser.parse_args()

    df = extract_table(args.input_pdf, page_num=args.page, lang=args.lang)
    export_to_excel(df, args.output_xlsx)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
