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
