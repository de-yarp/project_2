import pandas as pd
import pytest

from rates_stat.transform import get_api_agg


def test_agg_normal():
    input_df = pd.DataFrame(
        {
            "date": ["2025-01-01", "2025-01-02", "2025-01-03"] * 2,
            "currency_code": ["USD"] * 3 + ["GBP"] * 3,
            "rate": [1.10, 1.12, 1.11, 0.85, 0.86, 0.84],
            "base": ["EUR"] * 6,
        }
    )

    result = get_api_agg(input_df)

    # You calculated these yourself — you KNOW the right answer
    usd_row = result[result["currency_code"] == "USD"].iloc[0]
    assert usd_row["mean"] == pytest.approx(1.11, abs=1e-4)
    assert usd_row["min"] == 1.10
    assert usd_row["max"] == 1.12
    assert usd_row["volatility"] == pytest.approx(
        input_df[input_df["currency_code"] == "USD"]["rate"].std(), abs=1e-4
    )


def test_agg_single_date():
    input_df = pd.DataFrame(
        {
            "date": ["2025-01-01"] * 2,
            "currency_code": ["USD"] * 1 + ["GBP"] * 1,
            "rate": [1.10, 0.85],
            "base": ["EUR"] * 2,
        }
    )

    result = get_api_agg(input_df)

    # You calculated these yourself — you KNOW the right answer
    usd_row = result[result["currency_code"] == "USD"].iloc[0]
    assert usd_row["mean"] == pytest.approx(1.10, abs=1e-4)
    assert usd_row["min"] == 1.10
    assert usd_row["max"] == 1.10
    assert usd_row["volatility"] == 0
