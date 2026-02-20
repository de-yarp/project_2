import logging


def setup_logging(logger_name: str) -> logging.Logger:
    logger = logging.getLogger(logger_name)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
