"""Public API for GPT4All product demo utilities."""

from .diff import (
    DiffReport,
    ProductLine,
    diff_product_lines,
    parse_product_lines,
    extract_text_from_pdf,
)

__all__ = [
    "ProductLine",
    "DiffReport",
    "extract_text_from_pdf",
    "parse_product_lines",
    "diff_product_lines",
]
