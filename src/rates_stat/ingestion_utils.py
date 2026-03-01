import json
import logging

import pandas as pd

from .models import SchemaError

logger = logging.getLogger(__name__)


def get_schema_report(df: pd.DataFrame) -> None:
    row_num, col_num = df.shape
    cols = df.columns.to_list()
    cols_dtype = {col: df[col].dtype.name for col in cols}
    cols_missing = {col: int(df[col].isna().sum()) for col in cols}

    extra = {
        "row_count": row_num,
        "col_count": col_num,
        "columns": {"names": cols, "dtypes": cols_dtype, "missing_count": cols_missing},
    }

    logger.info(f"ingestion schema report: {json.dumps(extra, indent=2)}")


def validate_api_ingestion(
    df: pd.DataFrame, contract: dict, dt_count: int, cur_count: int
) -> None:
    try:
        assert contract["row_count"] == "DYNAMIC", (
            "api ingestion contract.row_count must be set to 'DYNAMIC', fixed row_count impossible"
        )
        req_row_count = dt_count * cur_count
        assert len(df) == req_row_count, (
            f"api response invalid row_count: {len(df)}, expected <{req_row_count}>"
        )

        col_info = contract["columns"]
        cols_req = pd.Index(col_info["required"])
        df_cols = df.columns

        duplicate_mask = df_cols.duplicated()
        duplicate_sample = df_cols[duplicate_mask]
        membership_mask = ~cols_req.isin(df_cols)

        assert not duplicate_mask.any(), (
            f"api response contains duplicate columns {duplicate_sample}"
        )
        assert not membership_mask.any(), (
            f"api response missing required columns: {cols_req[membership_mask]}"
        )

        date_fmt = col_info["date_fmt"]
        df["date"] = pd.to_datetime(df["date"], format=date_fmt, errors="coerce")
        missing_dates = df["date"].isna()
        assert not missing_dates.any(), (
            f"api response failed to convert dates: {missing_dates.sum()}"
        )

        for col, req_dtype in col_info["dtypes"].items():
            actual_dtype = df[col].dtype.name
            assert actual_dtype == req_dtype, (
                f"api response invalid dtype {{'{col}': '{actual_dtype}'}}, expected <{req_dtype}>"
            )

        for col, req_missing_rate in col_info["missing_percent"].items():
            missing_perc = round(df[col].isna().mean() * 100, 2)
            req_missing_perc = req_missing_rate / 100
            assert missing_perc <= req_missing_perc, (
                f"api response missing values percent {{ '{col}': {missing_perc} }} more than expected <{req_missing_perc}>"
            )

    except AssertionError as e:
        raise SchemaError(str(e)) from e
    except KeyError as e:
        msg = f"api response/contract missing column/key <{e.args[0]}>"
        raise SchemaError(msg) from e


def validate_legacy_ingestion(df: pd.DataFrame, contract: dict) -> None:
    try:
        req_row_count = contract["row_count"]
        assert len(df) == req_row_count, (
            f"legacy table invalid row_count: {len(df)}, expected <{req_row_count}>"
        )

        col_info = contract["columns"]
        cols_req = pd.Index(col_info["required"])
        df_cols = df.columns

        duplicate_mask = df_cols.duplicated()
        duplicate_sample = df_cols[duplicate_mask]
        membership_mask = ~cols_req.isin(df_cols)

        assert not duplicate_mask.any(), (
            f"legacy table contains duplicate columns {duplicate_sample}"
        )
        assert not membership_mask.any(), (
            f"legacy table missing required columns: {cols_req[membership_mask]}"
        )

        for col, req_dtype in col_info["dtypes"].items():
            actual_dtype = df[col].dtype.name
            assert actual_dtype == req_dtype, (
                f"legacy table invalid dtype {{'{col}': '{actual_dtype}'}}, expected <{req_dtype}>"
            )

        for col, req_missing_rate in col_info["missing_percent"].items():
            missing_perc = round(df[col].isna().mean() * 100, 2)
            req_missing_perc = req_missing_rate / 100
            assert missing_perc <= req_missing_perc, (
                f"legacy table missing values percent {{ '{col}': {missing_perc} }} more than expected <{req_missing_perc}>"
            )

    except AssertionError as e:
        raise SchemaError(str(e)) from e
    except KeyError as e:
        msg = f"legacy table/contract missing column/key <{e.args[0]}>"
        raise SchemaError(msg) from e


def validate_ingestion_contract(
    df_api: pd.DataFrame,
    df_legacy: pd.DataFrame,
    contract_api: dict,
    contract_legacy: dict,
    dt_count: int,
    cur_count: int,
) -> None:
    validate_api_ingestion(df_api, contract_api, dt_count, cur_count)

    validate_legacy_ingestion(df_legacy, contract_legacy)
