import logging


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)

    logger.setLevel(getattr(logging, level.upper()))

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger
