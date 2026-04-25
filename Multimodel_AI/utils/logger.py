"""
utils/logger.py — Centralized logging using Loguru
"""

import sys
import os
from loguru import logger


def setup_logger() -> None:
    logger.remove()

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Console handler
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>",
        colorize=True,
    )

    # Rotating file handler
    logger.add(
        "logs/app.log",
        level=log_level,
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} — {message}",
        enqueue=True,
    )

    logger.info("Logger initialized.")
