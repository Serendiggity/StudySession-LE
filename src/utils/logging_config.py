"""
Logging configuration for the Insolvency Study Assistant.
Sets up consistent logging across all modules.
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(log_level: str = None, log_file: str = None) -> logging.Logger:
    """
    Set up logging configuration for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                   If None, reads from LOG_LEVEL environment variable (default: INFO)
        log_file: Path to log file. If None, reads from LOG_FILE environment variable
                  (default: logs/insolvency_study.log)

    Returns:
        Logger instance configured for the application
    """
    # Get configuration from environment or use defaults
    log_level = log_level or os.getenv("LOG_LEVEL", "INFO")
    log_file = log_file or os.getenv("LOG_FILE", "logs/insolvency_study.log")

    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear any existing handlers
    root_logger.handlers.clear()

    # File handler with rotation (10MB max, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)

    # Console handler (simpler format)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Insolvency Study Assistant - Logging initialized")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Log file: {log_file}")
    logger.info("=" * 60)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Name of the module (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
