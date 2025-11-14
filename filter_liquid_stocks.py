"""
Filter Liquid Stocks - Select most actively traded stocks
This script filters the full stock list to keep only liquid stocks with good trading volume
"""
import os
import sys
import json
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Fix Windows console encoding
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def load_stock_list(filepath='data/us_stock_list.json'):
    """Load stock list from JSON"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data['tickers']


def filter_by_volume(tickers, min_volume=1_000_000, sample_days=5, batch_size=50):
    """
    Filter stocks by minimum average volume

    Args:
        tickers: List of ticker symbols
        min_volume: Minimum average daily volume (default: 1M shares)
        sample_days: Number of days to check
        batch_size: Download batch size

    Returns:
        list: Filtered ticker symbols with volume info
    """
    print(f"\n🔍 Filtering {len(tickers)} stocks by volume...")
    print(f"   Criteria: Avg volume >= {min_volume:,} shares/day")

    liquid_stocks = []
    total = len(tickers)

    # Process in batches
    for i in range(0, total, batch_size):
        batch = tickers[i:i+batch_size]
        print(f"\n📊 Processing batch {i//batch_size + 1}/{(total-1)//batch_size + 1} ({len(batch)} stocks)...")

        try:
            # Download recent data for batch
            df = yf.download(
                tickers=' '.join(batch),
                period=f'{sample_days}d',
                interval='1d',
                group_by='ticker',
                progress=False,
                threads=True
            )

            # Check each stock's volume
            for ticker in batch:
                try:
                    if len(batch) == 1:
                        stock_df = df
                    else:
                        stock_df = df[ticker]

                    if not stock_df.empty and 'Volume' in stock_df:
                        avg_volume = stock_df['Volume'].mean()

                        if avg_volume >= min_volume:
                            liquid_stocks.append({
                                'ticker': ticker,
                                'avg_volume': int(avg_volume),
                                'avg_volume_millions': round(avg_volume / 1_000_000, 2)
                            })
                            print(f"  ✅ {ticker}: {avg_volume/1_000_000:.2f}M shares/day")

                except Exception as e:
                    continue

        except Exception as e:
            print(f"  ❌ Batch error: {e}")
            continue

    print(f"\n✅ Found {len(liquid_stocks)} liquid stocks (out of {total})")
    return liquid_stocks


def main():
    """Main function"""
    print("=" * 60)
    print("💧 Liquid Stocks Filter")
    print("=" * 60)

    # Load full stock list
    print("\n📥 Loading full stock list...")
    all_tickers = load_stock_list()
    print(f"✅ Loaded {len(all_tickers)} stocks")

    # For testing, let's use a smaller sample first
    # Uncomment next line to test with only first 200 stocks
    # all_tickers = all_tickers[:200]

    # Filter by volume
    liquid_stocks = filter_by_volume(
        all_tickers,
        min_volume=1_000_000,  # 1M shares/day
        sample_days=5,
        batch_size=50
    )

    if not liquid_stocks:
        print("❌ No liquid stocks found")
        sys.exit(1)

    # Sort by volume (descending)
    liquid_stocks.sort(key=lambda x: x['avg_volume'], reverse=True)

    # Save results
    output_data = {
        'generated_at': datetime.now().isoformat(),
        'filter_criteria': {
            'min_volume': 1_000_000,
            'sample_days': 5
        },
        'total_count': len(liquid_stocks),
        'stocks': liquid_stocks
    }

    output_file = 'data/liquid_stocks.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n💾 Saved to: {output_file}")

    # Also save just ticker list for easy use
    ticker_only_data = {
        'generated_at': datetime.now().isoformat(),
        'total_count': len(liquid_stocks),
        'tickers': [s['ticker'] for s in liquid_stocks]
    }

    ticker_file = 'data/liquid_stocks_list.json'
    with open(ticker_file, 'w', encoding='utf-8') as f:
        json.dump(ticker_only_data, f, indent=2)

    print(f"💾 Ticker list saved to: {ticker_file}")

    # Show top 20
    print(f"\n📊 Top 20 most liquid stocks:")
    for i, stock in enumerate(liquid_stocks[:20], 1):
        print(f"   {i:2d}. {stock['ticker']:6s} - {stock['avg_volume_millions']:8.2f}M shares/day")

    print("\n" + "=" * 60)
    print(f"✅ Filter complete! {len(liquid_stocks)} liquid stocks found")
    print("=" * 60)


if __name__ == "__main__":
    main()
