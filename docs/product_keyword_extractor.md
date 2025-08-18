# Product Keyword Extractor

## Objective
Extract technical keywords from product descriptions to standardize data for Master Data Management or catalog cleanup.

## Input Format
- Excel file with columns `ItemID`, `ItemDescrEng1`, `ItemDescrEng2`

## Steps
1. **Load data** using pandas `read_excel` and combine the two description columns:
   ```python
   df = pd.read_excel(file_path)
   df["FullDescription"] = df["ItemDescrEng1"] + " " + df["ItemDescrEng2"].fillna("")
   ```
2. **Define keyword categories** as a dictionary where each category maps to a list of possible terms:
   ```python
   categories = {
       "Din": ["931", "934", "933"],
       "material": ["BRASS", "MS", "POLYAMIDE"],
       "kovuus": ["10.9", "8.8", "12.9"],
       "m": ["M5", "M6", "M8", "M10", "M12"],
       "Words": ["DACRO", "ZINCPL", "PLAIN", "DACLIT"],
   }
   ```
3. **Create a processing function** that searches each description for category terms and returns the first match per category:
   ```python
   import re

   def process_description(description: str) -> dict:
       keywords = {}
       if not isinstance(description, str):
           return keywords
       for category, terms in categories.items():
           for term in terms:
               if re.search(rf"\b{re.escape(term)}\b", description, re.IGNORECASE):
                   keywords[category] = term
                   break
       return keywords
   ```
4. **Apply keyword extraction** across all product descriptions:
   ```python
   df["Keywords"] = df["FullDescription"].apply(process_description)
   ```
5. **Optional – export results** to Excel for further use:
   ```python
   df.to_excel("cleaned_product_data.xlsx", index=False)
   ```

## Example Output
Parsing a description like `DIN 931 10.9 M6 x 50 ZINCPL` produces:
```python
{
    'Din': '931',
    'kovuus': '10.9',
    'm': 'M6',
    'Words': 'ZINCPL'
}
```
