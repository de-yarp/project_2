import logging
import sys


def setup_logging(logger_name: str) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(fmt="%(asctime)s | %(levelname)s | %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
