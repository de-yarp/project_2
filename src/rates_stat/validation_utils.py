import datetime as dt
from pathlib import Path

import holidays
import pandas as pd

from .models import AVAILABLE_CURRENCIES, Args, IOContractError


def validate_paths(fin: Path, fout: Path) -> None:
    try:
        if fin.stat().st_size == 0:
            msg = f"local_data: {str(fin)} is empty"
            raise IOContractError(msg)
    except FileNotFoundError:
        msg = f"local_data: {str(fin)} not found"
        raise IOContractError(msg)

    fout_parent = fout.parent
    if not fout_parent.exists():
        msg = f"out: parent dir {str(fout_parent)} not found"
        raise IOContractError(msg)
    if not fout_parent.is_dir():
        msg = f"out: parent {str(fout_parent)} is not a directory"
        raise IOContractError(msg)

    if fout.suffix != ".parquet":
        msg = f"out: invalid suffix '{str(fout.suffix)}', expected '.parquet'"
        raise IOContractError(msg)


def validate_currencies(base: str, pool: list[str]) -> None:
    if base not in AVAILABLE_CURRENCIES:
        msg = f"base: '{base}' not supported, see [uv run rates_stat info] for available currencies"
        raise IOContractError(msg)

    pool_set = set(pool)
    if not pool_set.issubset(AVAILABLE_CURRENCIES):
        msg = f"pool: contains unsupported currencies {list(pool_set - AVAILABLE_CURRENCIES)}, see [uv run rates_stat info] for available currencies"
        raise IOContractError(msg)


def normalize_dates(date_from: str, date_to: str) -> tuple[dt.date, dt.date, int]:
    dt_templates = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y.%m.%d",
        "%Y_%m_%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y",
        "%d_%m_%Y",
    ]

    dt_from = None
    dt_to = None
    for t in dt_templates:
        try:
            dt_from = dt.datetime.strptime(date_from, t)
            dt_to = dt.datetime.strptime(date_to, t)
            break
        except ValueError:
            continue
    else:
        msg = f"date_from/date_to: unsupported format {date_from}, {date_to}"
        raise IOContractError(msg)

    if dt_from > dt_to:
        msg = f"date_from/date_to: invalid positioning {date_from}, {date_to} date_from > date_to"
        raise IOContractError(msg)

    ecb_calendar = holidays.financial_holidays(
        "XECB", years=[y for y in range(dt_from.year, dt_to.year + 1)]
    )
    ecb_business_day = pd.offsets.CustomBusinessDay(holidays=list(ecb_calendar.keys()))

    # fallback in case dt_from is not a business day to always include a 1-business-day-before policy
    dt_from = ecb_business_day.rollback(dt_from)

    dt_range = pd.date_range(start=dt_from, end=dt_to, freq=ecb_business_day)
    if len(dt_range) < 1:
        msg = f"date_from/date_to: range ({dt_from.isoformat}..{dt_to.isoformat()}) is empty. \ntip: check for ECB holidays in range"
        raise IOContractError(msg)

    dt_from = dt_range[0].date()
    dt_to = dt_range[-1].date()

    return dt_from, dt_to, len(dt_range)


def normalize_currencies(base: str, pool: list[str]) -> tuple[str, list[str]]:
    base_norm = base.upper()
    pool_norm = [cur.upper() for cur in pool]

    return base_norm, pool_norm


def normalize_args(date_from: str, date_to: str, base: str, pool: list[str]) -> dict:
    dt_from, dt_to, dt_count = normalize_dates(date_from, date_to)
    base_norm, pool_norm = normalize_currencies(base, pool)

    return {
        "from": dt_from,
        "to": dt_to,
        "base": base_norm,
        "pool": pool_norm,
        "dt_count": dt_count,
    }


def validate_args(args: Args) -> None:
    validate_paths(args.local_data, args.out)

    validate_currencies(args.base, args.pool)


def post_transform_validate(df: pd.DataFrame) -> None:
    expected_columns = {
        "currency_code",
        "base",
        "date_from",
        "date_to",
        "mean",
        "min",
        "max",
        "volatility",
        "spread",
        "currency_name",
        "currency_group",
        "region",
        "sub_region",
        "is_major",
        "decimal_places",
    }
    assert len(df) > 0, "post-transform: df is empty"
    assert not df["currency_code"].isna().any(), (
        "post-transform: column 'currency_code' contains nulls"
    )
    assert not df["currency_code"].duplicated().any(), (
        "post-transform: column 'currency_code' is duplicated"
    )
    df_cols = set(df.columns)
    assert df_cols == expected_columns, (
        f"post-transform: missing columns {list(expected_columns - df_cols)}, extra columns {list(df_cols - expected_columns)}"
    )
    for col in ("mean", "min", "max", "volatility", "spread"):
        assert not df[col].isna().any(), (
            f"post-transform: column '{col}' contains nulls"
        )
