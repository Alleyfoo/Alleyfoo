# Toolbox Documentation

This folder will hold API reference and usage guides.

## Installation

```bash
pip install .
```

## Quickstart

```python
from toolbox.utils import hello_world
from toolbox.visualization import plot_scatter

print(hello_world())

import pandas as pd
df = pd.DataFrame({"x": [1,2,3], "y": [4,5,6]})
fig = plot_scatter(df, x="x", y="y", title="Example scatter")
fig.savefig("output.png")
```
