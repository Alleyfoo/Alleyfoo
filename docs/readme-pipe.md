# Pipe-transformation

Pipe transformation demo: simulate ingestion from AVS/SFTP, Azure Blob, or S3; standardize headers; and publish a warehouse view ready for Snowflake MERGE.

## Setup

- PowerShell:
  - `cd C:\Users\pertt\Alleyfoo\pipe-transformation`
  - `./scripts/setup.ps1`
  - In Jupyter, select kernel: `Python (pipe-transformation)`

## Run once (CLI)

- Transform using example config and write staged/exports to `simulated_storage`:
  - `./.venv/Scripts/python scripts/run_pipeline.py --run`
- List remote locations (from config):
  - `./.venv/Scripts/python scripts/run_pipeline.py --list`
- Fetch specific sources (requires credentials):
  - `./.venv/Scripts/python scripts/run_pipeline.py --fetch avs_orders`

Config lives at `config/pipeline.example.yaml`. Change `sources` to point at local files or switch a source to a remote connector (types: `azure_blob`, `s3`, `sftp`).

## Daily scheduling

- Windows Task Scheduler (example 02:00 daily):
  - Action (Program/script): `powershell.exe`
  - Arguments:
    - `-NoProfile -ExecutionPolicy Bypass -Command "cd 'C:\Users\pertt\Alleyfoo\pipe-transformation'; . .\.venv\Scripts\Activate.ps1; python scripts/run_pipeline.py --run"`

- Airflow (optional):
  - Convert steps into tasks (extract -> bronze -> silver -> warehouse) and schedule with `schedule_interval="0 2 * * *"`.

## Fetch examples

- Azure Blob (requires `AZURE_STORAGE_CONNECTION_STRING`):
  - In config set:
    ```yaml
    sources:
      avs_orders:
        type: azure_blob
        container: landing
        prefix: orders/
    ```
  - Then run: `./.venv/Scripts/python scripts/run_pipeline.py --fetch avs_orders`

- SFTP/AVS (private key auth):
  - In config set:
    ```yaml
    sources:
      avs_orders:
        type: sftp
        host: avs.company.local
        username: avs_sync
        key_path: C:/keys/avs_rsa
        remote_dir: /incoming/orders
    ```
  - Then run: `./.venv/Scripts/python scripts/run_pipeline.py --fetch avs_orders`

- S3 (AWS creds configured):
  - In config set:
    ```yaml
    sources:
      avs_orders:
        type: s3
        bucket: my-raw-bucket
        prefix: orders/
    ```
  - Then run: `./.venv/Scripts/python scripts/run_pipeline.py --fetch avs_orders`

After fetching, the transform step (`--run`) will also look in `simulated_storage/landing/<source>` if no explicit `path` is set, and pick the latest file automatically.

## Notebook

Open `simulated_pipeline_playbook.ipynb` for a visual walkthrough: standardization (Bronze→Silver), Snowflake COPY/MERGE SQL, header variants, incremental upsert, connector stubs, and config-driven demo.

## Snowflake: write_pandas

- Append:
  - `.\.venv\Scripts\python scripts\run_pipeline.py --run --write-snowflake append`
- Upsert via MERGE:
  - `.\.venv\Scripts\python scripts\run_pipeline.py --run --write-snowflake upsert`
- Set credentials via `.env` (see `.env.example`) or environment variables.

## .env

Copy `.env.example` to `.env` and fill as needed. The CLI auto-loads `.env` if present.

## Automation

- Windows Task Scheduler (02:00 daily)
  - Program: `powershell.exe`
  - Arguments:
    - `-NoProfile -ExecutionPolicy Bypass -Command "cd 'C:\Users\pertt\Alleyfoo\pipe-transformation'; . .\.venv\Scripts\Activate.ps1; python scripts\run_pipeline.py --run --write-snowflake upsert'"`
  - Or schedule the helper: `scripts\scheduled_run.ps1`
- GitHub Actions (nightly): see Section 18 in the notebook for a YAML outline.
- Airflow: convert steps to DAG tasks (extract -> bronze -> silver -> warehouse); example pseudo-DAG in the notebook.
