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
