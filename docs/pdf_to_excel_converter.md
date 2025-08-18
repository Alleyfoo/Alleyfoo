# PDF to Excel Converter

## Objective
Convert tabular pages from a PDF catalogue into a structured Excel file using OCR.

## Command-line execution
1. Install dependencies and the Tesseract OCR engine:
   ```bash
   pip install pymupdf pytesseract pillow pandas openpyxl pdfplumber
   sudo apt-get install -y tesseract-ocr
   ```
2. Run the notebook headlessly to produce `output.xlsx`:
   ```bash
   jupyter nbconvert --to notebook --execute Toolbox/notebooks/pdf_to_excel_converter.ipynb \
     --ExecutePreprocessor.timeout=600 --output executed.ipynb
   ```
   Adjust the variables at the top of the second cell before running:
   - `PDF_PATH`: path to the source PDF
   - `PAGE_NUM`: 1-based page index
   - `DPI`: rasterization resolution (e.g. `300`)
   - `OCR_LANG`: Tesseract language code (e.g. `eng`)
   - `CROP_BOX`: bounding box `(x0, y0, x1, y1)` for the table region
   - `OUT_XLSX`: location for the Excel file

## Sample input
Example settings used in the notebook:
```python
PDF_PATH = "/content/onepage.pdf"
PAGE_NUM = 1
DPI = 300
OCR_LANG = "eng"
CROP_BOX = (70.75448724699189, 109.77600105, 545.3519891000003, 215.16000375)
OUT_XLSX = "/content/output.xlsx"
```

## Excel output
The converter writes a workbook with a single sheet named `Jockey Wheels` containing:

- `Part nr.`
- `Description`
- `Max static load`
- `Max dynamic load`

Each row represents one entry from the catalogue table.
