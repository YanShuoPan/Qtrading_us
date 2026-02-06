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
    Update or insert stock price data to database using INSERT OR REPLACE

    Args:
        df: DataFrame containing code, date, open, high, low, close, volume columns
    """
    if df.empty:
        return

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Use INSERT OR REPLACE to handle duplicates
        records_inserted = 0
        for _, row in df.iterrows():
            cursor.execute(
                """
                INSERT OR REPLACE INTO prices(code, date, open, high, low, close, volume)
                VALUES(?, ?, ?, ?, ?, ?, ?)
                """,
                (row['code'], row['date'], row['open'], row['high'],
                 row['low'], row['close'], row['volume'])
            )
            records_inserted += 1

        conn.commit()

    logger.info(f"Data saved to database: {DB_PATH}, upserted {records_inserted} records")


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

    logger.info(f"Loaded {len(df)} records from database")

    if df.empty:
        logger.warning("Database is empty, no data to process")
        return pd.DataFrame()

    logger.info(f"DataFrame columns: {df.columns.tolist()}")
    logger.info(f"Date range in DB: {df['date'].min()} to {df['date'].max()}")

    cutoff = datetime.utcnow() - timedelta(days=days)
    df = df[df["date"] >= cutoff]

    logger.info(f"After filtering last {days} days: {len(df)} records")

    return df
