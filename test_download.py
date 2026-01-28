"""
Test script to verify stock data download
"""
import os
os.environ["US_STOCK_CODES"] = "AAPL,MSFT,GOOGL,AMZN,TSLA"

from modules.logger import setup_logger, get_logger
from modules.stock_data import fetch_prices_yf

setup_logger()
logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("Testing stock download with 5 major stocks...")

    test_codes = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

    try:
        df = fetch_prices_yf(test_codes, lookback_days=30)

        if not df.empty:
            logger.info(f"✅ Download successful!")
            logger.info(f"Total records: {len(df)}")
            logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
            logger.info(f"Stocks: {df['code'].unique().tolist()}")
        else:
            logger.warning("⚠️ Download returned empty DataFrame")

    except Exception as e:
        logger.error(f"❌ Download failed: {e}", exc_info=True)
