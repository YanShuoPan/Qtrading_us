"""
Stock data processing module - Download stock data and stock selection logic
"""
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import time
import random
from .database import get_existing_data_range
from .logger import get_logger

logger = get_logger(__name__)

# Configuration for batch downloading
BATCH_SIZE = 200  # Number of stocks per batch (increased from 150)
BATCH_DELAY_MIN = 2  # Minimum seconds between batches (reduced for speed)
BATCH_DELAY_MAX = 4  # Maximum seconds between batches (reduced for speed)
MAX_RETRIES = 3  # Maximum retry attempts per batch
INITIAL_DELAY = 1  # Initial delay before first batch to avoid burst


def fetch_prices_yf(codes, lookback_days=120) -> pd.DataFrame:
    """
    Download stock price data from Yahoo Finance with batch processing and retry mechanism

    Args:
        codes: List of stock ticker symbols
        lookback_days: Number of days to look back

    Returns:
        DataFrame: Stock price data
    """
    existing = get_existing_data_range()
    target_start = (datetime.utcnow() - timedelta(days=lookback_days * 2)).date().isoformat()

    codes_to_fetch = []
    for c in codes:
        c = c.strip()
        if not c:
            continue
        if c not in existing:
            codes_to_fetch.append(c)
            logger.debug(f"{c}: No historical data, need to download")
        else:
            max_date = existing[c]["max"]
            if max_date < datetime.utcnow().date().isoformat():
                codes_to_fetch.append(c)
                logger.debug(f"{c}: Data outdated (latest: {max_date}), need update")
            else:
                logger.debug(f"{c}: Data up to date (latest: {max_date})")

    if not codes_to_fetch:
        logger.info("All stock data is up to date, no download needed")
        return pd.DataFrame()

    logger.info(f"\n📊 Downloading {len(codes_to_fetch)} stocks in batches")
    logger.info(f"Period: {target_start} ~ today")
    logger.info(f"Batch size: {BATCH_SIZE} stocks per batch")

    # Split into batches
    num_batches = (len(codes_to_fetch) + BATCH_SIZE - 1) // BATCH_SIZE
    logger.info(f"Total batches: {num_batches}")

    all_results = []
    failed_stocks = []
    consecutive_failures = 0  # Track consecutive failures to adjust delays

    # Initial delay to avoid burst requests
    if num_batches > 1:
        logger.info(f"⏸️  Initial delay of {INITIAL_DELAY}s before starting batch downloads...")
        time.sleep(INITIAL_DELAY)

    for batch_idx in range(num_batches):
        start_idx = batch_idx * BATCH_SIZE
        end_idx = min((batch_idx + 1) * BATCH_SIZE, len(codes_to_fetch))
        batch_codes = codes_to_fetch[start_idx:end_idx]

        logger.info(f"\n🔄 Batch {batch_idx + 1}/{num_batches}: Processing {len(batch_codes)} stocks ({start_idx + 1}-{end_idx})")

        # Retry mechanism for each batch
        batch_success = False
        for attempt in range(MAX_RETRIES):
            try:
                # Add user agent to avoid being blocked
                import yfinance as yf_module
                if hasattr(yf_module, 'set_tz_cache_location'):
                    yf_module.set_tz_cache_location("/tmp/yfinance_cache")

                df = yf.download(
                    tickers=" ".join(batch_codes),
                    start=target_start,
                    interval="1d",
                    group_by="ticker",
                    auto_adjust=False,
                    progress=False,
                    threads=True,
                    timeout=30,
                )

                # Process downloaded data
                batch_out = []
                for c in batch_codes:
                    if isinstance(df, pd.DataFrame) and c in df:
                        tmp = df[c].reset_index().rename(columns=str.lower)

                        if "date" in tmp.columns and len(tmp) > 0:
                            tmp["date"] = pd.to_datetime(tmp["date"]).dt.tz_localize(None)
                            tmp["code"] = c
                            batch_out.append(tmp[["code", "date", "open", "high", "low", "close", "volume"]])
                            logger.debug(f"  ✓ {c}: {len(tmp)} records")
                        else:
                            logger.warning(f"  ✗ {c}: No valid data")
                            failed_stocks.append(c)
                    else:
                        logger.warning(f"  ✗ {c}: Not in response")
                        failed_stocks.append(c)

                if batch_out:
                    all_results.extend(batch_out)

                logger.info(f"  ✅ Batch {batch_idx + 1} completed: {len(batch_out)}/{len(batch_codes)} stocks successful")
                batch_success = True
                consecutive_failures = 0  # Reset failure counter on success
                break  # Success, exit retry loop

            except Exception as e:
                error_msg = str(e)
                logger.warning(f"  ⚠️ Batch {batch_idx + 1} attempt {attempt + 1}/{MAX_RETRIES} failed: {error_msg}")

                # Check if it's a JSON parsing error (API rate limit or empty response)
                if "Expecting value" in error_msg or "JSON" in error_msg:
                    logger.warning(f"  💡 Detected API rate limit or invalid response, increasing delay...")
                    retry_delay = (attempt + 1) * 5  # Longer delay for rate limit
                else:
                    retry_delay = (attempt + 1) * 3  # Standard exponential backoff

                if attempt < MAX_RETRIES - 1:
                    logger.info(f"  ⏳ Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"  ❌ Batch {batch_idx + 1} failed after {MAX_RETRIES} attempts")
                    logger.error(f"  📝 Error details: {error_msg}")
                    failed_stocks.extend(batch_codes)
                    consecutive_failures += 1

        # Add delay between batches (except for the last batch)
        if batch_idx < num_batches - 1:
            # Increase delay if there are consecutive failures
            delay_multiplier = 1 + (consecutive_failures * 0.5)  # +50% per failure
            base_delay = random.uniform(BATCH_DELAY_MIN, BATCH_DELAY_MAX)
            delay = base_delay * delay_multiplier

            if consecutive_failures > 0:
                logger.info(f"  ⏸️  Waiting {delay:.1f}s before next batch (extended due to {consecutive_failures} consecutive failures)...")
            else:
                logger.info(f"  ⏸️  Waiting {delay:.1f}s before next batch...")
            time.sleep(delay)

    # Combine all results
    result = pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()

    logger.info(f"\n✅ Download complete:")
    logger.info(f"  Total records: {len(result)}")
    logger.info(f"  Successful stocks: {len(codes_to_fetch) - len(failed_stocks)}/{len(codes_to_fetch)}")
    if failed_stocks:
        logger.warning(f"  Failed stocks ({len(failed_stocks)}): {', '.join(failed_stocks[:10])}" +
                      (f" and {len(failed_stocks) - 10} more..." if len(failed_stocks) > 10 else ""))

    if not result.empty and 'date' in result.columns:
        logger.info(f"  Date range: {result['date'].min()} ~ {result['date'].max()}")
        logger.info(f"  Unique dates: {result['date'].nunique()}")

    return result


def pick_stocks(prices: pd.DataFrame, top_k=12) -> pd.DataFrame:
    """
    Momentum stock selection strategy - Select stocks meeting criteria

    Strategy description:
    1. Exclude stocks with average volume < 1M shares in last 10 days
    2. Calculate MA20 (20-day moving average)
    3. Check last 5 days open and close prices average above MA20
    4. MA20 slope within reasonable range (< 2.0 for US market)
    5. Volatility control within 8% (US market typically more volatile)
    6. Average high-low range > $0.50 in last 10 days
    7. Price distance from MA20 within allowed range
    8. Group by MA20 slope, select stocks closest to MA20

    Args:
        prices: Stock price DataFrame
        top_k: Maximum number of stocks to return

    Returns:
        DataFrame: Stock selection results
    """
    if prices.empty:
        logger.warning("Input prices DataFrame is empty")
        return pd.DataFrame()

    # Validate required columns
    required_columns = ['code', 'date', 'open', 'high', 'low', 'close', 'volume']
    missing_columns = [col for col in required_columns if col not in prices.columns]
    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        logger.error(f"Available columns: {prices.columns.tolist()}")
        raise ValueError(f"DataFrame missing required columns: {missing_columns}")

    logger.info(f"Processing {len(prices)} price records for stock selection")
    logger.info(f"Unique stocks: {prices['code'].nunique()}")

    prices = prices.sort_values(["code", "date"])

    def add_feat(g):
        g = g.copy()
        g["ma20"] = g["close"].rolling(20, min_periods=20).mean()
        return g

    feat = prices.groupby("code", group_keys=False).apply(add_feat).reset_index(drop=True)

    # Ensure 'code' column is preserved
    if 'code' not in feat.columns and 'code' in prices.columns:
        logger.warning("'code' column lost after groupby, reconstructing...")
        # This shouldn't happen, but add safety check
        feat = prices.copy()
        feat["ma20"] = feat.groupby("code")["close"].transform(lambda x: x.rolling(20, min_periods=20).mean())

    logger.info(f"Features calculated, DataFrame has {len(feat)} records with columns: {feat.columns.tolist()}")

    results = []
    for code, group in feat.groupby("code"):
        group = group.sort_values("date")
        if len(group) < 10:
            continue

        # Check average volume > 1M shares in last 10 days
        last_10 = group.tail(10)
        avg_volume = last_10["volume"].mean()

        if avg_volume < 1_000_000:  # 1 million shares
            continue

        last_5 = group.tail(5)
        if last_5["ma20"].isna().any():
            continue

        # Check last 5 days average price above MA20
        avg_price_5d = (last_5["open"] + last_5["close"]) / 2
        price_above_ma20 = (avg_price_5d > last_5["ma20"]).all()

        if not price_above_ma20:
            continue

        # Average high-low range > $0.50 in last 10 days
        high_low_diff = last_10["high"] - last_10["low"]
        avg_high_low_diff = high_low_diff.mean()

        if avg_high_low_diff <= 0.5:
            continue

        # Calculate MA20 slope
        ma20_values = last_5["ma20"].values
        ma20_slope = (ma20_values[-1] - ma20_values[0]) / 4

        # Filter out stocks with excessive slope (adjusted for US market)
        if ma20_slope >= 2.0:
            continue

        # Calculate volatility
        price_std = last_5["close"].std()
        price_mean = last_5["close"].mean()
        volatility_pct = (price_std / price_mean * 100) if price_mean > 0 else 999
        if volatility_pct > 8.0:  # US market tolerance
            continue

        # Dynamic distance limit
        max_distance_allowed = max(3.0, volatility_pct * 1.5)

        # Calculate price distance from MA20
        min_price = last_5[["open", "close"]].min(axis=1)
        distance_pct = ((min_price - last_5["ma20"]) / last_5["ma20"] * 100)
        avg_distance = distance_pct.mean()

        if avg_distance > max_distance_allowed:
            continue

        # Calculate average distance from MA20
        avg_price = (last_5["open"] + last_5["close"]) / 2
        avg_ma20_distance = abs(avg_price - last_5["ma20"]).mean()

        # Check if last day is lowest close
        latest = last_5.iloc[-1]
        is_lowest_close = latest["close"] == last_5["close"].min()

        results.append({
            "code": code,
            "close": latest["close"],
            "ma20": latest["ma20"],
            "distance": avg_distance,
            "volatility": volatility_pct,
            "ma20_slope": ma20_slope,
            "max_distance": max_distance_allowed,
            "volume": latest["volume"],
            "avg_volume_10d": avg_volume,
            "avg_ma20_distance": avg_ma20_distance,
            "is_lowest_close": is_lowest_close
        })

    if not results:
        return pd.DataFrame()

    result_df = pd.DataFrame(results)

    # Group by MA20 slope
    group1 = result_df[(result_df["ma20_slope"] >= 0.8) & (result_df["ma20_slope"] < 2)]  # Strong trend
    group2 = result_df[result_df["ma20_slope"] < 0.8]  # Potential stocks

    # Group1: MA20 slope >= 0.8, select up to 6 stocks
    if len(group1) > 6:
        group1_filtered = group1[group1["is_lowest_close"] == False]
        if len(group1_filtered) > 6:
            group1 = group1_filtered.nsmallest(6, "avg_ma20_distance")
        elif len(group1_filtered) > 0:
            group1 = group1_filtered
        else:
            group1 = group1.nsmallest(6, "avg_ma20_distance")

    # Group2: MA20 slope < 0.8, select up to 6 stocks
    if len(group2) > 6:
        group2_filtered = group2[group2["is_lowest_close"] == False]
        if len(group2_filtered) > 6:
            group2 = group2_filtered.nsmallest(6, "avg_ma20_distance")
        elif len(group2_filtered) > 0:
            group2 = group2_filtered
        else:
            group2 = group2.nsmallest(6, "avg_ma20_distance")

    final_result = pd.concat([group1, group2], ignore_index=True)
    return final_result
