import datetime as dt  # noqa: F401

import pandas as pd


def response_to_dataframe(resp: dict) -> pd.DataFrame:
    base = resp.get("base", pd.NA)
    rates = resp.get("rates", pd.NA)

    rates_df = pd.DataFrame().from_dict(rates, orient="index")
    rates_df = rates_df.reset_index(names="date").melt(
        id_vars="date", var_name="currency", value_name="rate"
    )
    base_s = pd.Series([base for _ in range(len(rates_df))])
    rates_df["base"] = base_s
    # rates_df["date"] = pd.to_datetime(rates_df["date"], errors="coerce")

    return rates_df
