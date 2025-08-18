import subprocess
from pathlib import Path
import pandas as pd


def test_pdf_to_excel(tmp_path):
    script = Path(__file__).resolve().parent.parent / "scripts" / "pdf_to_excel_converter.py"
    input_pdf = Path(__file__).parent / "data" / "dummy_table.pdf"
    output_xlsx = tmp_path / "out.xlsx"

    subprocess.run(["python", str(script), str(input_pdf), str(output_xlsx)], check=True)

    df = pd.read_excel(output_xlsx)
    assert df.shape[0] == 1
    row = df.iloc[0]
    assert row["Part nr."] == "TP123"
    assert row["Description"].startswith("Sample") or row["Description"] == "Sample"
    assert row["Max static load"] == "10 kg"
    assert row["Max dynamic load"] == "20 kg"
