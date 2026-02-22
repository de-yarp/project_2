import logging

import pandas as pd

logger = logging.Logger(__name__)


def get_schema_report_api(df: pd.DataFrame) -> None:
    row_num, col_num = df.shape
    cols = df.columns.to_list()
    cols_dtype = {col: df[col].dtype.name for col in cols}
    cols_missing = {col: int(df[col].isna().sum()) for col in cols}

    extra = {
        "row_count": row_num,
        "col_count": col_num,
        "columns": {"names": cols, "dtypes": cols_dtype, "missing_count": cols_missing},
    }

    logger.info("ingestion schema report:", extra=extra)


def validate_api_ingestion(df: pd.DataFrame, contract: dict) -> None: ...


def validate_legacy_ingestion(df: pd.DataFrame, contract: dict) -> None: ...


def validate_ingestion_contract(df: pd.DataFrame, df_legacy: pd.DataFrame) -> None: ...
