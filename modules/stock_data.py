"""
Stock data processing module - Download stock data and stock selection logic
"""
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from .database import get_existing_data_range
from .logger import get_logger

logger = get_logger(__name__)


def fetch_prices_yf(codes, lookback_days=120) -> pd.DataFrame:
    """
    Download stock price data from Yahoo Finance

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
            logger.info(f"{c}: No historical data, need to download")
        else:
            max_date = existing[c]["max"]
            if max_date < datetime.utcnow().date().isoformat():
                codes_to_fetch.append(c)
                logger.info(f"{c}: Data outdated (latest: {max_date}), need update")
            else:
                logger.debug(f"{c}: Data up to date (latest: {max_date})")

    if not codes_to_fetch:
        logger.info("All stock data is up to date, no download needed")
        return pd.DataFrame()

    # For US stocks, no need to add suffix
    tickers = codes_to_fetch
    logger.info(f"\nDownloading {len(codes_to_fetch)} stocks")
    logger.info(f"Period: {target_start} ~ today")

    df = yf.download(
        tickers=" ".join(tickers),
        start=target_start,
        interval="1d",
        group_by="ticker",
        auto_adjust=False,
        progress=False,
    )

    logger.info(f"yfinance download complete, data type: {type(df)}, shape: {df.shape if hasattr(df, 'shape') else 'N/A'}")

    out = []
    for c in codes_to_fetch:
        if isinstance(df, pd.DataFrame) and c in df:
            tmp = df[c].reset_index().rename(columns=str.lower)
            logger.info(f"Stock {c}: Downloaded {len(tmp)} records")

            if "date" in tmp.columns:
                logger.info(f"Stock {c}: Original date type = {tmp['date'].dtype}, range = {tmp['date'].min()} ~ {tmp['date'].max()}")
                tmp["date"] = pd.to_datetime(tmp["date"]).dt.tz_localize(None)
                logger.info(f"Stock {c}: Converted date type = {tmp['date'].dtype}, range = {tmp['date'].min()} ~ {tmp['date'].max()}")
                logger.info(f"Stock {c}: Unique dates = {tmp['date'].nunique()}")

            tmp["code"] = c
            out.append(tmp[["code", "date", "open", "high", "low", "close", "volume"]])
        else:
            logger.warning(f"Stock {c}: Unable to retrieve data from yfinance")

    result = pd.concat(out, ignore_index=True) if out else pd.DataFrame()
    logger.info(f"Successfully downloaded {len(result)} records")
    if not result.empty and 'date' in result.columns:
        logger.info(f"Combined date range: {result['date'].min()} ~ {result['date'].max()}")
        logger.info(f"Combined unique dates: {result['date'].nunique()}")
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
        return pd.DataFrame()
    prices = prices.sort_values(["code", "date"])

    def add_feat(g):
        g = g.copy()
        g["ma20"] = g["close"].rolling(20, min_periods=20).mean()
        return g

    feat = prices.groupby("code", group_keys=False).apply(add_feat)

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
