# Product Description Keyword Extractor

## Objective
Identify predefined keyword categories in product descriptions.

## Main Functions
- `process_description(description: str, categories: Mapping[str, Sequence[str]]) -> dict[str, str]`
- `extract_keywords(df: pd.DataFrame, categories: Mapping[str, Sequence[str]], desc1: str = 'ItemDescrEng1', desc2: str | None = 'ItemDescrEng2') -> pd.DataFrame`

## Example
```python
import pandas as pd
from keywordextractor import extract_keywords

categories = {"Din": ["931"], "m": ["M5"], "Words": ["PLAIN"]}
frame = pd.DataFrame({
    "ItemID": [1],
    "ItemDescrEng1": ["DIN931 M5x20 PLAIN"],
    "ItemDescrEng2": [""],
})
result = extract_keywords(frame, categories)
print(result.loc[0, "Keywords"])
=======
# Product description keyword extractor

Utilities for pulling structured keywords from messy product descriptions.

## Example

```python
from productkeywords import extract_keywords_df
import pandas as pd

categories = {"m": ["M6"], "Din": ["931"]}

df = pd.DataFrame(
    {
        "ItemID": [1],
        "ItemDescrEng1": ["M6 Bolt"],
        "ItemDescrEng2": ["DIN931 10.9"],
    }
)

result = extract_keywords_df(df, categories)