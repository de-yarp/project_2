import sys
from pathlib import Path
from time import perf_counter
from typing import Annotated

import typer

from .log_utils import setup_logging
from .models import CURRENCIES_MAP, Args, IOContractError, SchemaError
from .pipeline import pipe_run
from .validation_utils import normalize_args, validate_args

logger = setup_logging("rates_stat")

app = typer.Typer()


@app.command()
def info():
    """prints available currencies"""
    print("--- ALL AVAILABLE CURRENCIES ---\n")
    for id, (k, v) in enumerate(CURRENCIES_MAP.items()):
        msg = f"{id}. '{k}': {v}"
        print(msg)


@app.command()
def run(
    date_from: Annotated[str, typer.Argument(..., help="date window: start")],
    date_to: Annotated[str, typer.Argument(..., help="date window: end")],
    base: Annotated[str, typer.Option(..., help="base currency")],
    pool: Annotated[
        list[str],
        typer.Option(..., help="pool of currencies to get exchange rates for"),
    ],
    local_data: Annotated[Path, typer.Argument(..., help="historical data")] = Path(
        "data"
    )
    / "input"
    / "legacy.csv",
    out: Annotated[Path, typer.Option(help="output path")] = Path("data")
    / "output"
    / "report.parquet",
    overwrite: Annotated[bool, typer.Option(help="idempotency switch")] = False,
):
    """runs the script"""
    try:
        args_norm = normalize_args(date_from, date_to, base, pool)
        args = Args(
            local_data,
            args_norm["from"],
            args_norm["to"],
            args_norm["base"],
            args_norm["pool"],
            out,
            overwrite,
            args_norm["dt_count"],
        )
        validate_args(args)

        if not args.overwrite and args.out.exists():
            msg = (
                f"overwrite: {args.out} exists, include '--overwrite' or change '--out'"
            )
            raise IOContractError(msg)

        logger.info(
            f"pipeline started(dates=[{args.date_from}...{args.date_to}], base='{args.base}', pool={args.pool}, legacy_path={args.local_data}, out_path={args.out}, overwrite={args.overwrite})"
        )
        t1 = perf_counter()
        pipe_run(args)
        logger.info(f"report saved {str(args.out)}: OK")
        t2 = perf_counter()
        logger.info(f"pipeline ended: took {round(t2 - t1, 3)}s")

        sys.exit(0)
    except (IOContractError, SchemaError) as e:
        logger.error(str(e))
        sys.exit(e.exit_code)
    except Exception as e:
        logger.exception(f"Unexpected error: {e.__class__.__qualname__}")
        sys.exit(1)
