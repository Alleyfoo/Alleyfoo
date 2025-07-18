#!/usr/bin/env bash
# Usage: bootstrap_repo.sh <repo-slug> <colab-url>
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <repo-slug> <colab-url>" >&2
  exit 1
fi

slug=$1
url=$2

mkdir -p "$slug"/{notebooks,src,data,tests,.github/workflows}
cd "$slug"

# Download notebook
notebook_name=$(basename "$url")
wget -q "$url" -O "notebooks/$notebook_name"

# Strip outputs
if command -v nbstripout >/dev/null 2>&1; then
  nbstripout "notebooks/$notebook_name"
fi

# Generate requirements
pipreqs --force --savepath requirements.txt . >/dev/null 2>&1 || true

# Default license and gitignore
cat <<'MIT' > LICENSE
MIT License

Copyright (c) $(date +%Y) Alleyfoo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
MIT

curl -sL https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore -o .gitignore

# Helper script to extract functions from notebook
cat <<'PY' > extract_functions.py
import re
import sys
import nbformat as nbf
from pathlib import Path

nb_path = Path(sys.argv[1])
nb = nbf.read(nb_path, as_version=4)
source_lines = []
for cell in nb.cells:
    if cell.cell_type == "code":
        if re.search(r"^\s*(def |class )", cell.source, re.MULTILINE):
            source_lines.append(cell.source)

Path("src").mkdir(exist_ok=True)
(Path("src") / "core.py").write_text("\n\n".join(source_lines))
PY

# Minimal smoke test
cat <<'PY' > tests/test_smoke.py
import importlib

def test_import():
    module = importlib.import_module('src.core')
    assert hasattr(module, '__file__')
PY

# GitHub Actions workflow
cat <<'YML' > .github/workflows/python.yml
name: Python package

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pip install pytest
      - run: pytest -q
YML

# README template
cat <<'TEMPLATE' > README_template.md
# {{ project_title }}
**Short one-sentence tagline**

| Section | Summary |
|---------|---------|
| **Problem** | {{ problem }} |
| **Solution** | {{ solution }} |
| **Key libraries** | {{ tech }} |
| **Try it** | `python -m src.cli --help` |

## Quick start
```bash
pip install -r requirements.txt
python notebooks/{{ notebook_name }}
```
Sample output
(insert screenshot or small gif)

{{ project_title }} – FI
(Finnish translation here)
TEMPLATE

# README rendering helper
cat <<'PY' > render_readme.py
from pathlib import Path
import argparse
from jinja2 import Template
import json

parser = argparse.ArgumentParser()
parser.add_argument('--config', required=True)
args = parser.parse_args()

cfg = json.loads(Path(args.config).read_text())

tmpl = Template(Path('README_template.md').read_text())
Path('README.md').write_text(tmpl.render(**cfg))
PY

cd ..

printf '\nRepository skeleton created in %s\n' "$slug"

