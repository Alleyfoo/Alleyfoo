# PDF to Excel Converter

## Objective
Convert tabular regions in PDFs into structured Excel worksheets using OCR.

## Main Functions
- `parse_ocr_text_to_df(text: str) -> pd.DataFrame`: parse OCR output into a table.
- `extract_pdf_table(pdf_path, page_num, crop_box, dpi=300, ocr_lang="eng") -> pd.DataFrame`: rasterize a PDF region and run OCR.
- `save_table_to_excel(df, out_path, sheet_name="Sheet1")`: save the parsed table to an Excel file.

## Example
```python
from pdf2excel import extract_pdf_table, save_table_to_excel

bbox = (70.7, 109.7, 545.3, 215.16)
df = extract_pdf_table("catalog.pdf", page_num=1, crop_box=bbox)
save_table_to_excel(df, "output.xlsx", sheet_name="Jockey Wheels")
```
