from pathlib import Path
from typing import Annotated

import typer

from .log_utils import setup_logging
from .models import Args
from .validation_utils import normalize_args, validate_args

logger = setup_logging("rates_stat")

app = typer.Typer()


@app.command()
def info():
    """prints available currencies"""
    # for id, (k, v) in enumerate(CURRENCIES_MAP.items()):
    #     msg = f"{id}. [{k}]: {v}"
    #     logger.info(msg)
    ...


@app.command()
def run(
    local_data: Annotated[Path, typer.Argument(..., help="historical data")],
    date_from: Annotated[str, typer.Argument(..., help="date window: start")],
    date_to: Annotated[str, typer.Argument(..., help="date window: end")],
    base: Annotated[str, typer.Option(..., help="base currency")],
    pool: Annotated[
        list[str],
        typer.Option(..., help="pool of currencies to get exchange rates for"),
    ],
    out: Annotated[Path, typer.Option(help="output path")] = Path("data") / "output",
    overwrite: Annotated[bool, typer.Option(help="idempotency switch")] = False,
):
    args_norm = normalize_args(date_from, date_to, base, pool)
    args = Args(
        local_data,
        args_norm["to"],
        args_norm["from"],
        args_norm["base"],
        args_norm["pool"],
        out,
        overwrite,
    )
    validate_args(args)
    ...
