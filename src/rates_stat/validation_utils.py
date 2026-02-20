import datetime as dt  # noqa: F401
from pathlib import Path

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


def normalize_dates(date_from: str, date_to: str) -> tuple[dt.date, dt.date]:
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
            dt_from = dt.datetime.strptime(date_from, t).date()
            dt_to = dt.datetime.strptime(date_to, t).date()
            break
        except ValueError:
            continue
    else:
        msg = f"date_from/date_to: unsupported format {date_from}, {date_to}"
        raise IOContractError(msg)

    if dt_from > dt_to:
        msg = f"date_from/date_to: invalid position {date_from}, {date_to} date_from > date_to"
        raise IOContractError(msg)

    return dt_from, dt_to


def normalize_currencies(base: str, pool: list[str]) -> tuple[str, list[str]]:
    base_norm = base.upper()
    pool_norm = [cur.upper() for cur in pool]

    return base_norm, pool_norm


def normalize_args(date_from: str, date_to: str, base: str, pool: list[str]) -> dict:
    dt_from, dt_to = normalize_dates(date_from, date_to)
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
