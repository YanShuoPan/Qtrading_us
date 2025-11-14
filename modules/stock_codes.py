"""
Stock codes module - Manage US stock symbols
"""
import os
import json
from .logger import get_logger

logger = get_logger(__name__)

# Popular US stocks (S&P 100 components and other major stocks)
DEFAULT_US_STOCKS = [
    # Technology
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "NVDA", "TSLA", "AVGO", "ORCL",
    "ADBE", "CRM", "CSCO", "ACN", "AMD", "IBM", "INTC", "QCOM", "TXN", "INTU",
    "NOW", "PANW", "AMAT", "ADI", "MU", "LRCX", "KLAC", "SNPS", "CDNS", "MCHP",

    # Healthcare
    "UNH", "JNJ", "LLY", "ABBV", "MRK", "TMO", "ABT", "DHR", "PFE", "BMY",
    "AMGN", "MDT", "GILD", "ISRG", "VRTX", "CVS", "CI", "ELV", "ZTS", "REGN",

    # Financial Services
    "BRK.B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "AXP", "BLK",
    "SPGI", "C", "CB", "SCHW", "MMC", "PGR", "AON", "TFC", "USB", "PNC",

    # Consumer Cyclical
    "AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "LOW", "TJX", "BKNG", "CMG",
    "F", "GM", "MAR", "ABNB", "HLT", "DHI", "LEN", "NVR", "PHM", "DRI",

    # Consumer Defensive
    "WMT", "PG", "KO", "PEP", "COST", "MDLZ", "PM", "MO", "CL", "KMB",
    "GIS", "HSY", "K", "SYY", "KHC", "MNST", "CLX", "CHD", "TSN", "CAG",

    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HES",
    "WMB", "KMI", "HAL", "BKR", "FANG", "DVN", "PXD", "EQT", "CTRA", "MRO",

    # Industrials
    "BA", "HON", "UNP", "RTX", "UPS", "CAT", "LMT", "GE", "DE", "GD",
    "NOC", "MMM", "ETN", "ITW", "EMR", "CSX", "NSC", "WM", "FDX", "CARR",

    # Communication Services
    "GOOGL", "META", "NFLX", "DIS", "CMCSA", "T", "VZ", "TMUS", "CHTR", "EA",
    "ATVI", "TTWO", "WBD", "PARA", "OMC", "IPG", "LYV", "NWSA", "FOX", "FOXA",

    # Real Estate
    "AMT", "PLD", "CCI", "EQIX", "PSA", "SPG", "O", "WELL", "DLR", "AVB",
    "EQR", "VICI", "VTR", "ARE", "INVH", "MAA", "ESS", "UDR", "EXR", "CPT",

    # Utilities
    "NEE", "DUK", "SO", "D", "AEP", "SRE", "EXC", "XEL", "ED", "PEG",
    "WEC", "ES", "DTE", "FE", "ETR", "AWK", "PPL", "EIX", "AEE", "CMS",

    # Materials
    "LIN", "APD", "SHW", "ECL", "DD", "NEM", "FCX", "NUE", "DOW", "CTVA",
    "VMC", "MLM", "ALB", "PPG", "EMN", "IFF", "CE", "FMC", "MOS", "CF",
]

# Stock names dictionary (ticker -> full name)
STOCK_NAMES = {
    # Technology
    "AAPL": "Apple Inc", "MSFT": "Microsoft", "GOOGL": "Alphabet A", "GOOG": "Alphabet C",
    "AMZN": "Amazon", "META": "Meta Platforms", "NVDA": "NVIDIA", "TSLA": "Tesla",
    "AVGO": "Broadcom", "ORCL": "Oracle", "ADBE": "Adobe", "CRM": "Salesforce",
    "CSCO": "Cisco", "ACN": "Accenture", "AMD": "AMD", "IBM": "IBM",
    "INTC": "Intel", "QCOM": "Qualcomm", "TXN": "Texas Instruments", "INTU": "Intuit",

    # Healthcare
    "UNH": "UnitedHealth", "JNJ": "Johnson & Johnson", "LLY": "Eli Lilly", "ABBV": "AbbVie",
    "MRK": "Merck", "TMO": "Thermo Fisher", "ABT": "Abbott Labs", "DHR": "Danaher",
    "PFE": "Pfizer", "BMY": "Bristol Myers", "AMGN": "Amgen", "MDT": "Medtronic",

    # Financial
    "BRK.B": "Berkshire Hathaway", "JPM": "JPMorgan Chase", "V": "Visa", "MA": "Mastercard",
    "BAC": "Bank of America", "WFC": "Wells Fargo", "GS": "Goldman Sachs", "MS": "Morgan Stanley",
    "AXP": "American Express", "BLK": "BlackRock", "SPGI": "S&P Global", "C": "Citigroup",

    # Consumer Cyclical
    "HD": "Home Depot", "MCD": "McDonald's", "NKE": "Nike", "SBUX": "Starbucks",
    "LOW": "Lowe's", "TJX": "TJX Companies", "BKNG": "Booking Holdings", "CMG": "Chipotle",
    "F": "Ford", "GM": "General Motors", "MAR": "Marriott", "ABNB": "Airbnb",

    # Consumer Defensive
    "WMT": "Walmart", "PG": "Procter & Gamble", "KO": "Coca-Cola", "PEP": "PepsiCo",
    "COST": "Costco", "MDLZ": "Mondelez", "PM": "Philip Morris", "MO": "Altria",

    # Energy
    "XOM": "Exxon Mobil", "CVX": "Chevron", "COP": "ConocoPhillips", "SLB": "Schlumberger",
    "EOG": "EOG Resources", "MPC": "Marathon Petroleum", "PSX": "Phillips 66", "VLO": "Valero",

    # Industrials
    "BA": "Boeing", "HON": "Honeywell", "UNP": "Union Pacific", "RTX": "Raytheon",
    "UPS": "UPS", "CAT": "Caterpillar", "LMT": "Lockheed Martin", "GE": "General Electric",
    "DE": "Deere & Co", "GD": "General Dynamics", "NOC": "Northrop Grumman", "MMM": "3M",

    # Communication
    "NFLX": "Netflix", "DIS": "Disney", "CMCSA": "Comcast", "T": "AT&T",
    "VZ": "Verizon", "TMUS": "T-Mobile", "CHTR": "Charter Comm", "EA": "Electronic Arts",

    # Real Estate
    "AMT": "American Tower", "PLD": "Prologis", "CCI": "Crown Castle", "EQIX": "Equinix",
    "PSA": "Public Storage", "SPG": "Simon Property", "O": "Realty Income", "WELL": "Welltower",

    # Utilities
    "NEE": "NextEra Energy", "DUK": "Duke Energy", "SO": "Southern Co", "D": "Dominion",
    "AEP": "American Electric", "SRE": "Sempra Energy", "EXC": "Exelon", "XEL": "Xcel Energy",

    # Materials
    "LIN": "Linde", "APD": "Air Products", "SHW": "Sherwin-Williams", "ECL": "Ecolab",
    "DD": "DuPont", "NEM": "Newmont", "FCX": "Freeport-McMoRan", "NUE": "Nucor",
}


def load_stock_list_from_json(filepath='data/us_stock_list.json'):
    """
    Load stock list from JSON file

    Args:
        filepath: Path to JSON file

    Returns:
        list: Stock ticker symbols, or None if file doesn't exist
    """
    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tickers = data.get('tickers', [])
            logger.info(f"Loaded {len(tickers)} stocks from {filepath}")
            logger.info(f"  Generated at: {data.get('generated_at', 'Unknown')}")
            return tickers
    except Exception as e:
        logger.warning(f"Failed to load {filepath}: {e}")
        return None


def get_stock_codes():
    """
    Get stock codes list with priority:
    1. Environment variable US_STOCK_CODES
    2. JSON file (data/us_stock_list.json)
    3. Default hardcoded list

    Returns:
        list: Stock ticker symbols
    """
    # Priority 1: Custom codes from environment variable
    custom_codes = os.environ.get("US_STOCK_CODES", "").strip()
    if custom_codes:
        codes = [c.strip() for c in custom_codes.split(",") if c.strip()]
        logger.info(f"Using custom stock list from env: {len(codes)} stocks")
        return codes

    # Priority 2: Load from JSON file
    json_codes = load_stock_list_from_json()
    if json_codes:
        logger.info(f"Using stock list from JSON: {len(json_codes)} stocks")
        return json_codes

    # Priority 3: Default hardcoded list
    logger.info(f"Using default hardcoded stock list: {len(DEFAULT_US_STOCKS)} stocks")
    return DEFAULT_US_STOCKS


def get_stock_name(code: str) -> str:
    """
    Get stock full name by ticker symbol

    Args:
        code: Stock ticker symbol

    Returns:
        str: Stock full name
    """
    return STOCK_NAMES.get(code, code)


def get_picks_top_k() -> int:
    """
    Get maximum number of stocks to select

    Returns:
        int: Top K value
    """
    return int(os.environ.get("TOP_K", "12"))
