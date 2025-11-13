"""
Database operations module - Handle stock price data
"""
import os
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from .config import DB_PATH, DATA_DIR, DEBUG_MODE
from .logger import get_logger

logger = get_logger(__name__)


# ===== Database Initialization =====

def ensure_db():
    """Create stock price table"""
    # Ensure directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS prices(
                code TEXT,
                date TEXT,
                open REAL, high REAL, low REAL, close REAL,
                volume INTEGER,
                PRIMARY KEY(code, date)
            )
            """
        )
        conn.commit()
    logger.info(f"Database initialized: {DB_PATH}")


# ===== Stock Price Data Management =====

def get_existing_data_range() -> dict:
    """Get date range of each stock in database"""
    if not os.path.exists(DB_PATH):
        return {}
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT code, MIN(date) as min_date, MAX(date) as max_date FROM prices GROUP BY code"
        )
        result = {}
        for row in cursor:
            result[row[0]] = {"min": row[1], "max": row[2]}
    return result


def upsert_prices(df: pd.DataFrame):
    """
    Update or insert stock price data to database

    Args:
        df: DataFrame containing code, date, open, high, low, close, volume columns
    """
    if df.empty:
        return
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)

    with sqlite3.connect(DB_PATH) as conn:
        # Create temporary table
        df.to_sql("_prices_in", conn, if_exists="replace", index=False)

        # Delete existing records that match
        conn.execute("DELETE FROM prices WHERE (code, date) IN (SELECT code, date FROM _prices_in)")

        # Insert new/updated records
        conn.execute(
            """
            INSERT INTO prices(code, date, open, high, low, close, volume)
            SELECT code, date, open, high, low, close, volume FROM _prices_in
            """
        )

        # Clean up temporary table
        conn.execute("DROP TABLE IF EXISTS _prices_in")
        conn.commit()

    logger.info(f"Data saved to database: {DB_PATH}, updated {len(df)} records")


def load_recent_prices(days=120) -> pd.DataFrame:
    """
    Load recent N days stock price data from database

    Args:
        days: Number of days

    Returns:
        DataFrame: Stock price data
    """
    if not os.path.exists(DB_PATH):
        logger.warning(f"Database not found: {DB_PATH}")
        return pd.DataFrame()

    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(
            "SELECT code, date, open, high, low, close, volume FROM prices",
            conn,
            parse_dates=["date"],
        )
    cutoff = datetime.utcnow() - timedelta(days=days)
    df = df[df["date"] >= cutoff]
    return df
