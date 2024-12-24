import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # file_handler = logging.FileHandler(f"logs/{datetime.now().strftime('%Y-%m-%d')}.log")
    # file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # INACTIVE FOR NOW
    # logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
