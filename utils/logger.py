"""
Application Logger
Sets up logging configuration for console and file output
"""

import logging
import sys
from pathlib import Path

def setup_logger():
    """Configure and return the logger instance."""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger("app_logger")
    logger.setLevel(logging.INFO)
    
    # Check if handlers already exist to prevent duplicate logs
    if logger.hasHandlers():
        return logger
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File Handler
    file_handler = logging.FileHandler(log_dir / "resume_analyzer.log", encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()