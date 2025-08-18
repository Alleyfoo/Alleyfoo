def test_import():
    import pdf2excel  # noqa: F401


def test_parse_rows():
    from pdf2excel import parse_ocr_text_to_df

    text = "TP123 Sample part | 100 kg 80 kg"
    df = parse_ocr_text_to_df(text)
    assert not df.empty
    assert df.loc[0, "Part nr."] == "TP123"


def test_parse_empty():
    from pdf2excel import parse_ocr_text_to_df

    df = parse_ocr_text_to_df("")
    assert df.empty
