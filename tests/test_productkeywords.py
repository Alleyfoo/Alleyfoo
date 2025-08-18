import pytest

pd = pytest.importorskip("pandas")

from productkeywords import extract_keywords_df, process_description


def test_import():
    import productkeywords  # noqa: F401


def test_extract_keywords_df_basic():
    df = pd.DataFrame(
        {
            "ItemID": [1],
            "ItemDescrEng1": ["M6 Bolt"],
            "ItemDescrEng2": ["DIN931 10.9"],
        }
    )
    categories = {"m": ["M5", "M6"], "Din": ["931"]}
    out = extract_keywords_df(df, categories)
    assert out.loc[0, "Keywords"]["m"] == "M6"
    assert out.loc[0, "Keywords"]["Din"] == "931"


def test_process_description_non_string():
    assert process_description(None, {"m": ["M5"]}) == {}
