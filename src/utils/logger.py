"""
src/utils/logger.py

Logging utility for the
N100 Financial Intelligence Platform.
"""

import logging
from pathlib import Path

# -------------------------------------------------------
# Create log directory
# -------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOG_DIR = PROJECT_ROOT / "output" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "application.log"

# -------------------------------------------------------
# Logger Configuration
# -------------------------------------------------------

logger = logging.getLogger("N100")

logger.setLevel(logging.INFO)

if not logger.handlers:

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s"
    )

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def info(message: str):
    logger.info(message)


def warning(message: str):
    logger.warning(message)


def error(message: str):
    logger.error(message)


def debug(message: str):
    logger.debug(message)


if __name__ == "__main__":

    info("Logger initialized successfully.")
    warning("Logger warning example.")
    error("Logger error example.")