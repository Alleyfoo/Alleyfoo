# GPT4All Product Demo

## Setup
- Install dependencies in the notebook:
  ```bash
  pip install gpt4all pydantic pandas numpy openpyxl rapidfuzz pdfplumber pillow pytesseract pdf2image requests
  apt-get install poppler-utils tesseract-ocr
  ```
- The demo works without API keys or HF tokens. The notebook automatically downloads the small GPT4All model `orca-mini-3b-gguf2-q4_0.gguf` on first run.
- Default configuration also fetches the IKEA BESTÅ PDF for testing.

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
