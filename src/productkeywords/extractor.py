"""Utilities for extracting keywords from product descriptions."""

from __future__ import annotations

import re
from typing import Dict, List

try:  # pragma: no cover - optional dependency
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore


def process_description(
    description: str | None, categories: Dict[str, List[str]]
) -> Dict[str, str]:
    """Extract first matching term for each category from a description.

    Args:
        description: Free-form product description.
        categories: Mapping of category names to lists of candidate terms.

    Returns:
        Mapping of categories to the first matching term found in the description.
    """

    keywords: Dict[str, str] = {}
    if not isinstance(description, str):
        return keywords
    for category, terms in categories.items():
        for term in terms:
            if re.search(rf"\b{re.escape(term)}\b", description, re.IGNORECASE):
                keywords[category] = term
                break
    return keywords


def extract_keywords_df(
    df: "pd.DataFrame",
    categories: Dict[str, List[str]],
    descr1_col: str = "ItemDescrEng1",
    descr2_col: str = "ItemDescrEng2",
) -> "pd.DataFrame":
    """Add combined description and keyword extraction columns to ``df``.

    Args:
        df: DataFrame containing at least ``ItemID`` and description columns.
        categories: Mapping of category names to lists of candidate terms.
        descr1_col: Name of the first description column.
        descr2_col: Name of the second description column.

    Returns:
        DataFrame with ``ItemID``, ``FullDescription``, and ``Keywords`` columns.
    """

    if pd is None:  # pragma: no cover - import guard
        raise ImportError("pandas is required for extract_keywords_df")

    temp = df.copy()
    temp["FullDescription"] = (
        temp[descr1_col].fillna("").astype(str)
        + " "
        + temp[descr2_col].fillna("").astype(str)
    ).str.strip()
    temp["Keywords"] = temp["FullDescription"].apply(
        lambda d: process_description(d, categories)
    )
    return temp[["ItemID", "FullDescription", "Keywords"]]
