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
```
