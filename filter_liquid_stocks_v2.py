"""
Filter Liquid Stocks V2 - Improved version with better error handling
Select most actively traded stocks with progress tracking
"""
import os
import sys
import json
import time
import yfinance as yf
import pandas as pd
from datetime import datetime

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


def load_progress(filepath='data/filter_progress.json'):
    """Load progress from previous run"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return {'processed': [], 'results': []}
    return {'processed': [], 'results': []}


def save_progress(progress, filepath='data/filter_progress.json'):
    """Save progress"""
    with open(filepath, 'w') as f:
        json.dump(progress, f, indent=2)


def check_single_stock(ticker, min_volume=1_000_000, sample_days=5):
    """
    Check single stock volume

    Args:
        ticker: Stock ticker symbol
        min_volume: Minimum average daily volume
        sample_days: Number of days to check

    Returns:
        dict or None: Stock info if meets criteria
    """
    try:
        # Download data for single stock
        stock = yf.Ticker(ticker)
        df = stock.history(period=f'{sample_days}d')

        if df.empty or len(df) < 3:  # Need at least 3 days
            return None

        # Calculate average volume
        avg_volume = df['Volume'].mean()

        if avg_volume >= min_volume:
            return {
                'ticker': ticker,
                'avg_volume': int(avg_volume),
                'avg_volume_millions': round(avg_volume / 1_000_000, 2),
                'days_checked': len(df)
            }

        return None

    except Exception as e:
        # Silently skip errors (many stocks may be delisted or have issues)
        return None


def filter_by_volume_incremental(tickers, min_volume=1_000_000, sample_days=5,
                                 resume=True, save_interval=50):
    """
    Filter stocks by volume with incremental progress saving

    Args:
        tickers: List of ticker symbols
        min_volume: Minimum average daily volume
        sample_days: Number of days to check
        resume: Resume from previous progress
        save_interval: Save progress every N stocks

    Returns:
        list: Filtered ticker symbols with volume info
    """
    print(f"\n🔍 Filtering stocks by volume...")
    print(f"   Criteria: Avg volume >= {min_volume:,} shares/day")
    print(f"   Sample days: {sample_days}")

    # Load previous progress if resuming
    if resume:
        progress = load_progress()
        processed_tickers = set(progress['processed'])
        liquid_stocks = progress['results']
        print(f"   📂 Resuming: {len(processed_tickers)} already processed")
    else:
        processed_tickers = set()
        liquid_stocks = []

    # Filter out already processed
    remaining = [t for t in tickers if t not in processed_tickers]
    total = len(tickers)
    already_done = len(processed_tickers)

    print(f"   📊 Total: {total}, Done: {already_done}, Remaining: {len(remaining)}")
    print(f"   💾 Progress saved every {save_interval} stocks")
    print()

    # Process remaining stocks
    for idx, ticker in enumerate(remaining, 1):
        # Check stock
        result = check_single_stock(ticker, min_volume, sample_days)

        if result:
            liquid_stocks.append(result)
            print(f"  ✅ {ticker:6s} - {result['avg_volume_millions']:8.2f}M shares/day ({already_done + idx}/{total})")
        else:
            # Only show progress every 10 stocks to avoid spam
            if idx % 10 == 0:
                print(f"  ⏳ Progress: {already_done + idx}/{total} ({(already_done + idx)/total*100:.1f}%)", end='\r')

        # Update progress
        processed_tickers.add(ticker)

        # Save progress periodically
        if idx % save_interval == 0:
            save_progress({
                'processed': list(processed_tickers),
                'results': liquid_stocks,
                'last_updated': datetime.now().isoformat()
            })
            print(f"\n  💾 Progress saved: {len(liquid_stocks)} liquid stocks found so far")

        # Small delay to avoid rate limiting
        time.sleep(0.1)

    # Final save
    save_progress({
        'processed': list(processed_tickers),
        'results': liquid_stocks,
        'last_updated': datetime.now().isoformat(),
        'completed': True
    })

    print(f"\n\n✅ Found {len(liquid_stocks)} liquid stocks (out of {total})")
    return liquid_stocks


def main():
    """Main function"""
    print("=" * 60)
    print("💧 Liquid Stocks Filter V2")
    print("=" * 60)

    # Load full stock list
    print("\n📥 Loading full stock list...")
    all_tickers = load_stock_list()
    print(f"✅ Loaded {len(all_tickers)} stocks")

    # Ask user if they want to test with a sample
    print("\n⚠️  Processing all stocks will take 2-3 hours!")
    print("   Options:")
    print("   1. Test with first 100 stocks (~5 minutes)")
    print("   2. Test with first 500 stocks (~20 minutes)")
    print("   3. Process all stocks (~2-3 hours)")
    print("   4. Resume previous progress")

    choice = input("\nEnter choice (1-4) [default: 1]: ").strip() or "1"

    if choice == "1":
        all_tickers = all_tickers[:100]
        print(f"\n🧪 Testing with first 100 stocks")
        resume = False
    elif choice == "2":
        all_tickers = all_tickers[:500]
        print(f"\n🧪 Testing with first 500 stocks")
        resume = False
    elif choice == "3":
        print(f"\n⚡ Processing all {len(all_tickers)} stocks")
        resume = False
    else:
        print(f"\n🔄 Resuming previous progress")
        resume = True

    # Filter by volume
    liquid_stocks = filter_by_volume_incremental(
        all_tickers,
        min_volume=1_000_000,  # 1M shares/day
        sample_days=5,
        resume=resume,
        save_interval=50
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

    # Show statistics
    print(f"\n📈 Volume Statistics:")
    volumes = [s['avg_volume_millions'] for s in liquid_stocks]
    print(f"   Max:     {max(volumes):.2f}M shares/day")
    print(f"   Median:  {pd.Series(volumes).median():.2f}M shares/day")
    print(f"   Min:     {min(volumes):.2f}M shares/day")

    print("\n" + "=" * 60)
    print(f"✅ Filter complete! {len(liquid_stocks)} liquid stocks found")
    print("=" * 60)

    # Clean up progress file
    if os.path.exists('data/filter_progress.json'):
        os.remove('data/filter_progress.json')
        print("\n🗑️  Progress file cleaned up")


if __name__ == "__main__":
    main()
