from __future__ import annotations

import re
from typing import Mapping, Sequence

import pandas as pd


def process_description(
    description: str, categories: Mapping[str, Sequence[str]]
) -> dict[str, str]:
    """Extract keywords from a product description.

    Args:
        description: Product description string to scan.
        categories: Mapping of category name to possible search terms.

    Returns:
        A mapping of categories to the first matching term in ``description``.
        Categories without matches are omitted.
    """
    keywords: dict[str, str] = {}
    if not isinstance(description, str):
        return keywords

    for category, terms in categories.items():
        for term in terms:
            pattern = rf"\b{re.escape(term)}\b"
            if re.search(pattern, description, flags=re.IGNORECASE):
                keywords[category] = term
                break
    return keywords


def extract_keywords(
    df: pd.DataFrame,
    categories: Mapping[str, Sequence[str]],
    desc1: str = "ItemDescrEng1",
    desc2: str | None = "ItemDescrEng2",
) -> pd.DataFrame:
    """Add keyword extraction results to a DataFrame.

    The function combines description columns and applies :func:`process_description`.

    Args:
        df: Input DataFrame containing description columns.
        categories: Mapping of category name to search terms.
        desc1: Name of the primary description column.
        desc2: Optional name of the secondary description column.

    Returns:
        A copy of ``df`` with ``FullDescription`` and ``Keywords`` columns.

    Raises:
        KeyError: If ``desc1`` is not present in ``df``.
    """
    work = df.copy()
    if desc1 not in work.columns:
        raise KeyError(f"Column '{desc1}' not found")

    first = work[desc1].fillna("")
    if desc2 and desc2 in work.columns:
        second = work[desc2].fillna("")
        work["FullDescription"] = first + " " + second
    else:
        work["FullDescription"] = first

    work["Keywords"] = work["FullDescription"].apply(lambda d: process_description(d, categories))
    return work
