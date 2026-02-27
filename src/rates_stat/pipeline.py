import logging

from .ingestion_utils import get_schema_report, validate_ingestion_contract
from .io_utils import load_contract, read_legacy, safe_write_parquet
from .models import (
    API_INGESTION_CONTRACT_PATH,
    LEGACY_INGESTION_CONTRACT_PATH,
    Args,
)
from .request_core import get_rates
from .transform import merge_and_aggregate, response_to_dataframe

logger = logging.getLogger(__name__)


def pipe_run(args: Args) -> None:
    response = get_rates(args.base, args.pool, args.date_from, args.date_to)
    logger.info("fetch: OK")
    df_api = response_to_dataframe(response)
    logger.info("response -> dataframe: OK")
    get_schema_report(df_api)
    api_contract = load_contract(API_INGESTION_CONTRACT_PATH)

    df_legacy = read_legacy(args.local_data)
    logger.info("legacy data: OK")
    get_schema_report(df_legacy)
    legacy_contract = load_contract(LEGACY_INGESTION_CONTRACT_PATH)

    validate_ingestion_contract(
        df_api,
        df_legacy,
        api_contract,
        legacy_contract,
        args.dt_count,
        len(args.pool),
    )
    logger.info("ingestion contract validation: OK")

    df_merged = merge_and_aggregate(df_api, df_legacy)
    logger.info("aggregation & merge: OK")
    safe_write_parquet(df_merged, args.out)
