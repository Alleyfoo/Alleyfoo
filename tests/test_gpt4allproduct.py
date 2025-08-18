def test_import():
    import gpt4allproduct  # noqa: F401


def test_parse_product_lines():
    from gpt4allproduct import parse_product_lines

    text = "111.222.33 shelf 30×20\nnotes\n222.333.44 door M4x10"
    lines = parse_product_lines(text)
    assert len(lines) == 2
    assert lines[0].sku.startswith("111.222.33")


def test_diff_product_lines_stub():
    from gpt4allproduct import ProductLine, diff_product_lines

    class Stub:
        def generate(self, prompt, max_tokens=512, temp=0.1):
            return '{"is_changed": true, "differences": ["size"], "confidence": 0.9}'

    orig = ProductLine("sku1", "Shelf 30x20")
    curr = ProductLine("sku1", "Shelf 35x20")
    report = diff_product_lines(orig, curr, model=Stub())
    assert report.is_changed
    assert report.differences == ["size"]


def test_diff_product_lines_bad_json():
    import pytest
    from gpt4allproduct import ProductLine, diff_product_lines

    class BadStub:
        def generate(self, prompt, max_tokens=512, temp=0.1):
            return "not json"

    orig = ProductLine("sku1", "Shelf")
    curr = ProductLine("sku1", "Shelf")
    with pytest.raises(ValueError):
        diff_product_lines(orig, curr, model=BadStub())
