from pathlib import Path

import pandas as pd
import requests

from rates_stat.ingestion_utils import get_schema_report, validate_ingestion_contract
from rates_stat.io_utils import load_contract
from rates_stat.models import (
    API_INGESTION_CONTRACT_PATH,
    LEGACY_INGESTION_CONTRACT_PATH,
)
from rates_stat.request_core import get_rates
from rates_stat.transform import merge_and_aggregate, response_to_dataframe
from rates_stat.validation_utils import normalize_dates


def get_available_cur_pool() -> None:
    curs = requests.get("https://api.frankfurter.dev/v1/currencies").json()
    print(curs.keys())


if __name__ == "__main__":
    legacy_path = Path("data") / "input" / "legacy.csv"
    dt_from, dt_to, dt_count = normalize_dates("2025-11-23", "2025-11-29")
    base = "EUR"
    pool = ["PLN", "HUF"]
    cur_count = len(pool)

    # api_contract_path = Path("config") / "ingestion_contract_api.json"
    # legacy_contract_path = Path("config") / "ingestion_contract_legacy.json"

    resp = get_rates(base, pool, dt_from, dt_to)
    df_api = response_to_dataframe(resp)
    print(df_api)
    # report = get_schema_report(df_api)
    # print(report)

    df_legacy = pd.read_csv(legacy_path)
    report_legacy = get_schema_report(df_legacy)
    # print(report_legacy)

    api_contract = load_contract(API_INGESTION_CONTRACT_PATH)
    legacy_contract = load_contract(LEGACY_INGESTION_CONTRACT_PATH)

    # print(dt_count, cur_count)
    validate_ingestion_contract(
        df_api, df_legacy, api_contract, legacy_contract, dt_count, cur_count
    )
    print("OK\n")
    # print(df_api.info())
    df_merged = merge_and_aggregate(df_api, df_legacy)

    print(df_merged)
    print(df_merged.info())
    print(df_merged.columns.duplicated().any())
