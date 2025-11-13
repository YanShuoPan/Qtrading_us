"""
Configuration module - Centralized environment variable management
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ===== Debug Settings =====
DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"

# ===== Database Settings =====
DATA_DIR = os.environ.get("DATA_DIR", "data")
DB_PATH = os.path.join(DATA_DIR, "us_stocks.sqlite")

# ===== Stock Selection Settings =====
# Maximum number of stocks to select
TOP_K = int(os.environ.get("TOP_K", "12"))

# Lookback period for historical data (in days)
LOOKBACK_DAYS = int(os.environ.get("LOOKBACK_DAYS", "120"))

# ===== Output Settings =====
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "output")
