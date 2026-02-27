import logging

import pandas as pd

logger = logging.getLogger(__name__)


def response_to_dataframe(resp: dict) -> pd.DataFrame:
    base = resp.get("base", pd.NA)
    rates = resp.get("rates", pd.NA)

    rates_df = pd.DataFrame().from_dict(rates, orient="index")
    rates_df = rates_df.reset_index(names="date").melt(
        id_vars="date", var_name="currency_code", value_name="rate"
    )
    base_s = pd.Series([base for _ in range(len(rates_df))])
    rates_df["base"] = base_s

    return rates_df


def get_api_agg(df: pd.DataFrame) -> pd.DataFrame:
    df_agg = (
        df.groupby(by=["currency_code", "base"])
        .agg(
            date_from=pd.NamedAgg(column="date", aggfunc="min"),
            date_to=pd.NamedAgg(column="date", aggfunc="max"),
            mean=pd.NamedAgg(column="rate", aggfunc="mean"),
            min=pd.NamedAgg(column="rate", aggfunc="min"),
            max=pd.NamedAgg(column="rate", aggfunc="max"),
            volatility=pd.NamedAgg(column="rate", aggfunc="std"),
        )
        .reset_index()
    )
    df_agg["spread"] = df_agg["max"] - df_agg["min"]

    if df_agg["date_from"].iloc[0] == df_agg["date_to"].iloc[0]:
        logger.warning(
            "aggregation & merge: date range contains only 1 value -> report.volatility set to 0!"
        )
        df_agg.fillna({"volatility": 0}, inplace=True)

    return df_agg


def merge_api_agg_legacy(df_agg: pd.DataFrame, df_legacy: pd.DataFrame) -> pd.DataFrame:
    return df_agg.merge(df_legacy, how="left", on="currency_code").sort_values(
        by="currency_code"
    )


def merge_and_aggregate(df_api: pd.DataFrame, df_legacy: pd.DataFrame) -> pd.DataFrame:
    df_agg = get_api_agg(df_api)

    return merge_api_agg_legacy(df_agg, df_legacy)
