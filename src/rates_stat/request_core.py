import datetime as dt
import logging
from time import perf_counter  # noqa: F401

import requests as req
from requests.exceptions import ConnectionError, HTTPError, Timeout  # noqa: F401
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.Logger(__name__)

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def is_retryable(response: req.Response) -> bool:
    return response.status_code in RETRYABLE_STATUS_CODES


@retry(
    wait=wait_exponential(multiplier=1, min=1, max=60),
    stop=stop_after_attempt(5),
    retry=(
        retry_if_exception_type((ConnectionError, Timeout))
        | retry_if_result(is_retryable)
    ),
    reraise=True,
)
def fetch_rates(
    base: str, pool: list[str], dt_from: dt.date, dt_to: dt.date
) -> req.Response:
    date_from = dt_from.isoformat()
    date_to = dt_to.isoformat()
    url = f"https://api.frankfurter.dev/v1/{date_from}..{date_to}?base={base}&symbols={','.join(pool)}"

    try:
        resp = req.get(url, timeout=(3, 5))
        if resp.status_code not in RETRYABLE_STATUS_CODES:
            resp.raise_for_status()
    except ConnectionError as e:
        msg = "server unreachable"
        raise ConnectionError(msg) from e
    except Timeout as e:
        msg = "5 retry attempts used up"
        raise Timeout(msg) from e
    except HTTPError as e:
        msg = f"client error {e.response.status_code}"
        raise HTTPError(msg) from e

    return resp
