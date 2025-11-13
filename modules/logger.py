"""
Logging module - Configure logging system
"""
import logging
from .config import DEBUG_MODE

def setup_logger():
    """Setup logging system"""
    if DEBUG_MODE:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            handlers=[
                logging.FileHandler('debug.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        print(f"🐛 DEBUG mode enabled, detailed logs will be saved to debug.log")
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    logger = logging.getLogger(__name__)
    logger.info("=== US Stocks Autobot Started ===")
    logger.info(f"DEBUG_MODE: {DEBUG_MODE}")

    return logger

def get_logger(name=__name__):
    """Get logger instance"""
    return logging.getLogger(name)
