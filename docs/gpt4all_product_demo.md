# GPT4All Product Demo

Python utilities for spotting changes in product descriptions with a local GPT4All model.

## Setup
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- The demo works without API keys or HF tokens. The default GPT4All model `orca-mini-3b-gguf2-q4_0.gguf` downloads on first use.
- Default configuration also fetches the IKEA BESTÅ PDF for testing.

## Main Functions
- `extract_text_from_pdf(path, page_index=0) -> str`: read text from a PDF page with an OCR fallback.
- `parse_product_lines(text: str) -> list[ProductLine]`: pick likely product lines and synthesize SKUs.
- `diff_product_lines(orig: ProductLine, curr: ProductLine, model=None) -> DiffReport`: compare two lines using GPT4All.

## Example
```python
from gpt4all import GPT4All
from gpt4allproduct import ProductLine, diff_product_lines

model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")
orig = ProductLine("123.456.78-01", "Shelf 30×20 cm")
curr = ProductLine("123.456.78-01", "Shelf 35×20 cm")
report = diff_product_lines(orig, curr, model)
print(report.differences)
```

## Execution
1. Adjust configuration variables such as `USE_DEFAULT_PDF`, `PAGE_INDEX`, and `GPT4ALL_MODEL`.
2. Download the default PDF or upload your own, then extract text from the selected page with an OCR fallback.
3. Parse the lines into `sku` and `description` columns. The notebook introduces random typos or size tweaks to simulate changes.
4. For each original/current pair, the local model is prompted with:
   ```
   System: Compare two product lines. Output ONLY valid JSON: {"is_changed":bool,"differences":list of short strings,"confidence":0-1,"notes":optional}.
   User: Original: {orig}
   Current: {curr}
   Rules: JSON only. If unsure, set is_changed=false with low confidence.
   ```
5. The responses are parsed into a `DiffReport` structure and merged with the dataset.
6. Results are saved as CSV and XLSX files named `zero_setup_ikea_diff_<timestamp>.{csv,xlsx}`.

## Expected Output
- A table with columns like `sku`, `description`, `is_changed`, `differences`, `confidence`, and `notes`.
- Exported CSV and Excel files in the Colab `/content` directory.
- The demo is intended for experimentation; JSON accuracy improves with larger GPT4All models.
