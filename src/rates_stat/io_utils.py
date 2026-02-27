import json
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .models import SchemaError
from .validation_utils import post_transform_validate

logger = logging.getLogger(__name__)


def load_contract(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_legacy(path: Path = Path("data") / "input" / "legacy.csv") -> pd.DataFrame:
    return pd.read_csv(path)


def safe_write_parquet(df: pd.DataFrame, path: Path) -> None:
    try:
        post_transform_validate(df)
    except AssertionError as e:
        raise SchemaError(str(e))
    logger.info("post-transform validation: OK")
    table: pa.Table = pa.Table.from_pandas(df)

    tmp_path = None
    try:
        with NamedTemporaryFile(delete=False, dir=path.parent) as tmp:
            tmp_path = Path(tmp.name)

        pq.write_table(table, tmp_path)
        tmp_path.replace(path)
        logger.info(f"report: row_count={table.shape[0]}, col_count={table.shape[1]}")

    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
