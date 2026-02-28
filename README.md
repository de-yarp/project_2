# Purpose
Pipeline that merges API currency rates and local data, computes summary statistics per currency over a configurable lookback window, and writes the result as a stable Parquet file.


## CLI Usage
```bash
uv run rates_stat run <date_from> <date_to> [local_data] --base <code> --pool <code> [--pool <code> ...] [--out <path>] [--overwrite]
```

### Arguments

| Arg | Default | Description |
|---|---|---|
| `date_from` | *required* | Date window start (e.g. `2024-01-01`) |
| `date_to` | *required* | Date window end (e.g. `2024-06-30`) |
| `local_data` | `data/input/legacy.csv` | Path to historical data |

### Options

| Flag | Default | Description |
|---|---|---|
| `--base` | *required* | Base currency (e.g. `EUR`) |
| `--pool` | *required* | Target currencies (repeat for multiple) |
| `--out` | `data/output/report.parquet` | Output path |
| `--overwrite` | `False` | Idempotency switch — overwrite existing output |

### Example
```bash
uv run rates_stat run 2024-01-01 2024-06-30 \
  --base EUR \
  --pool USD --pool GBP --pool CZK \
  --out data/output/report.parquet \
  --overwrite
```

## How it works

**Ingestion contract rationale**. All columns are required. Missing policy is 'raise on nulls' for the API response, no tolerance. The core logic requires every column present in other case the result will become corrupted. Legacy data covers every available currency the API can provide, therefore i don't expect any nulls.

**Merge strategy**. Left join picked. Legacy data is treated as secondary, so if it doesn't contain a currency or contains a null - it is not important for the result. The priority is to deliver the core currency rates statistics.

**Aggregation choices**. Basic metrics: mean, min, max, volatility. These are the core metrics I'm familiar with, other may be implemented on need. Single date is handled exactly like a normal case, just that the volatility is set to 0.

**Safe-write reasoning**. The safe-write pattern implemented prevents incomplete binary from being written. .parquet is a binary file with metadata, so it's practically useless if corrupted.
