import pandas as pd

from keywordextractor import extract_keywords, process_description


def test_import():
    assert callable(extract_keywords)
    assert callable(process_description)


def test_extract_keywords():
    df = pd.DataFrame(
        {
            "ItemDescrEng1": ["DIN931 M5x20 PLAIN"],
            "ItemDescrEng2": [""],
        }
    )
    categories = {"Din": ["931"], "m": ["M5", "M6"], "Words": ["PLAIN"]}
    out = extract_keywords(df, categories)
    assert out.loc[0, "Keywords"] == {"Din": "931", "m": "M5", "Words": "PLAIN"}


def test_non_string_description():
    df = pd.DataFrame({"ItemDescrEng1": [None]})
    categories = {"m": ["M5"]}
    out = extract_keywords(df, categories)
    assert out.loc[0, "Keywords"] == {}
