"""
Update US Stock List from NASDAQ
Downloads the latest stock symbols from NASDAQ and other exchanges
"""
import os
import sys
import json
import pandas as pd
from datetime import datetime

# Fix Windows console encoding
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def fetch_all_tickers():
    """
    Fetch all US stock tickers from NASDAQ official files

    Returns:
        list: Sorted list of ticker symbols
    """
    print("📥 Downloading stock list from NASDAQ...")

    # Official NASDAQ files
    nasdaq_url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
    other_url = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"

    try:
        # Read NASDAQ listed stocks
        df1 = pd.read_csv(nasdaq_url, sep='|')
        print(f"✅ NASDAQ listed: {len(df1)} records")

        # Read other exchange stocks
        df2 = pd.read_csv(other_url, sep='|')
        print(f"✅ Other exchanges: {len(df2)} records")

        # Combine both dataframes
        tickers = pd.concat([
            df1[['Symbol']],
            df2[['ACT Symbol']].rename(columns={'ACT Symbol': 'Symbol'})
        ])

        # Remove NaN values first
        tickers = tickers.dropna()

        # Clean up - remove last row "File Creation Time" and keep only alphabetic symbols
        tickers = tickers[tickers['Symbol'].str.match(r'^[A-Z]+$', na=False)]

        # Get unique sorted list
        ticker_list = sorted(tickers['Symbol'].unique().tolist())

        print(f"📊 Total unique tickers: {len(ticker_list)}")

        return ticker_list

    except Exception as e:
        print(f"❌ Error fetching tickers: {e}")
        return []


def filter_tickers(tickers, min_length=1, max_length=5, exclude_patterns=None):
    """
    Filter ticker symbols based on criteria

    Args:
        tickers: List of ticker symbols
        min_length: Minimum symbol length
        max_length: Maximum symbol length
        exclude_patterns: List of patterns to exclude (e.g., ['TEST', 'ZZZZ'])

    Returns:
        list: Filtered ticker list
    """
    if exclude_patterns is None:
        exclude_patterns = []

    filtered = []
    for ticker in tickers:
        # Length filter
        if len(ticker) < min_length or len(ticker) > max_length:
            continue

        # Exclude patterns
        if any(pattern in ticker for pattern in exclude_patterns):
            continue

        filtered.append(ticker)

    return filtered


def save_to_json(tickers, filename='data/us_stock_list.json'):
    """
    Save ticker list to JSON file

    Args:
        tickers: List of ticker symbols
        filename: Output JSON filename
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    data = {
        'generated_at': datetime.now().isoformat(),
        'total_count': len(tickers),
        'tickers': tickers
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"💾 Saved to: {filename}")


def main():
    """Main function"""
    print("=" * 60)
    print("🇺🇸 US Stock List Updater")
    print("=" * 60)

    # Fetch all tickers
    all_tickers = fetch_all_tickers()

    if not all_tickers:
        print("❌ Failed to fetch tickers")
        sys.exit(1)

    # Show sample
    print(f"\n📋 Sample tickers: {all_tickers[:20]}")

    # Filter tickers (optional)
    print("\n🔍 Filtering tickers...")
    print("   Criteria: 1-5 characters, alphabetic only")

    filtered_tickers = filter_tickers(
        all_tickers,
        min_length=1,
        max_length=5,
        exclude_patterns=['TEST', 'ZZZZ']  # Exclude test symbols
    )

    print(f"✅ Filtered count: {len(filtered_tickers)}")

    # Save to file
    save_to_json(filtered_tickers, 'data/us_stock_list.json')

    # Also save all tickers
    save_to_json(all_tickers, 'data/us_stock_list_all.json')

    print("\n" + "=" * 60)
    print("✅ Stock list updated successfully!")
    print(f"📊 Filtered list: {len(filtered_tickers)} tickers")
    print(f"📊 Complete list: {len(all_tickers)} tickers")
    print("=" * 60)

    # Show statistics
    print("\n📈 Statistics:")
    print(f"   1-char symbols: {len([t for t in filtered_tickers if len(t) == 1])}")
    print(f"   2-char symbols: {len([t for t in filtered_tickers if len(t) == 2])}")
    print(f"   3-char symbols: {len([t for t in filtered_tickers if len(t) == 3])}")
    print(f"   4-char symbols: {len([t for t in filtered_tickers if len(t) == 4])}")
    print(f"   5-char symbols: {len([t for t in filtered_tickers if len(t) == 5])}")


if __name__ == "__main__":
    main()
