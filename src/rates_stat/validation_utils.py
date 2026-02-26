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

    if not fout.exists():
        msg = f"out: {str(fout)} not found"
        raise IOContractError(msg)
    if not fout.is_dir():
        msg = f"out: {str(fout)} is not a directory"
        raise IOContractError(msg)


def validate_currencies(base: str, pool: list[str]) -> None:
    if base not in AVAILABLE_CURRENCIES:
        msg = "base: unsupported, see [uv run rates_stat info] for available currencies"
        raise IOContractError(msg)

    if not set(pool).issubset(AVAILABLE_CURRENCIES):
        msg = "pool: contains unsupported currencies, see [uv run rates_stat info] for available currencies"


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
    dt_from, dt_to, _ = normalize_dates(date_from, date_to)
    base_norm, pool_norm = normalize_currencies(base, pool)

    return {
        "from": dt_from,
        "to": dt_to,
        "base": base_norm,
        "pool": pool_norm,
    }


def validate_args(args: Args) -> None:
    validate_paths(args.local_data, args.out)

    validate_currencies(args.base, args.pool)
