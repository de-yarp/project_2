import datetime as dt

import requests

from rates_stat.request_core import get_rates
from rates_stat.schema_report import get_schema_report_api
from rates_stat.transform import response_to_dataframe


def get_available_cur_pool() -> None:
    curs = requests.get("https://api.frankfurter.dev/v1/currencies").json()
    print(curs.keys())


if __name__ == "__main__":
    dt_from = dt.date.fromisoformat("2025-11-23")
    dt_to = dt.date.fromisoformat("2025-11-29")
    base = "EUR"
    pool = ["PLN", "HUF"]
    resp = get_rates(base, pool, dt_from, dt_to)
    df = response_to_dataframe(resp)
    print(df)
    report = get_schema_report_api(df)
    print(report)
