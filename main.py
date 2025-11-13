"""
US Stocks Autobot - Main Program
Use momentum strategy to select US stocks and generate reports with charts
"""
import os
import json
import shutil
from datetime import datetime, timedelta

# Import modules
from modules.logger import setup_logger, get_logger
from modules.config import TOP_K, LOOKBACK_DAYS
from modules.database import (
    ensure_db,
    upsert_prices,
    load_recent_prices
)
from modules.stock_codes import get_stock_codes, get_stock_name, get_picks_top_k
from modules.stock_data import fetch_prices_yf, pick_stocks
from modules.visualization import plot_stock_charts
from modules.html_generator import generate_daily_html, generate_index_html

# Initialize logger
setup_logger()
logger = get_logger(__name__)


def main():
    """Main program flow"""
    logger.info("=" * 50)
    logger.info("🚀 US Stocks Autobot Execution Started")
    logger.info("=" * 50)
    start_time = datetime.now()

    try:
        # ===== Step 1: Initialize Database =====
        logger.info("\n📌 Step 1: Initialize Database")
        ensure_db()

        # ===== Step 2: Download Stock Data =====
        logger.info("\n📌 Step 2: Download Stock Data")
        codes = get_stock_codes()
        df_new = fetch_prices_yf(codes, lookback_days=LOOKBACK_DAYS)
        if not df_new.empty:
            upsert_prices(df_new)
            logger.info("✅ Database updated")
        else:
            logger.info("ℹ️  No need to update database")

        # ===== Step 3: Load Data and Select Stocks =====
        logger.info("\n📌 Step 3: Load Data and Select Stocks")
        hist = load_recent_prices(days=LOOKBACK_DAYS)
        top_k = get_picks_top_k()

        if hist.empty:
            logger.warning("⚠️ No historical data available")
            return

        picked = pick_stocks(hist, top_k=top_k)

        if picked.empty:
            logger.info("📊 No stocks meet the selection criteria today")
            return

        # ===== Step 4: Group and Display Results =====
        logger.info("\n📌 Step 4: Stock Selection Results")

        # Group stocks by MA20 slope
        group1 = picked[(picked["ma20_slope"] >= 0.8) & (picked["ma20_slope"] < 2)]
        group2 = picked[picked["ma20_slope"] < 0.8]

        group1_codes = group1["code"].tolist()
        group2_codes = group2["code"].tolist()

        logger.info(f"\n🔥 Strong Momentum Group (MA20 slope >= 0.8):")
        logger.info(f"   Total: {len(group1_codes)} stocks")
        if group1_codes:
            for idx, row in group1.iterrows():
                stock_name = get_stock_name(row['code'])
                logger.info(
                    f"   - {row['code']} {stock_name}: "
                    f"Close=${row['close']:.2f}, MA20=${row['ma20']:.2f}, "
                    f"Slope={row['ma20_slope']:.3f}, Vol={row['volatility']:.2f}%"
                )

        logger.info(f"\n👀 Potential Stocks Group (MA20 slope < 0.8):")
        logger.info(f"   Total: {len(group2_codes)} stocks")
        if group2_codes:
            for idx, row in group2.iterrows():
                stock_name = get_stock_name(row['code'])
                logger.info(
                    f"   - {row['code']} {stock_name}: "
                    f"Close=${row['close']:.2f}, MA20=${row['ma20']:.2f}, "
                    f"Slope={row['ma20_slope']:.3f}, Vol={row['volatility']:.2f}%"
                )

        # ===== Step 5: Generate Charts =====
        logger.info("\n📌 Step 5: Generate Stock Charts")

        chart_files = []

        if group1_codes:
            logger.info(f"\n📊 Generating charts for Strong Momentum Group...")
            chart1_path = plot_stock_charts(
                group1_codes,
                hist,
                output_filename=f"strong_momentum_{datetime.now().strftime('%Y%m%d')}.png"
            )
            if chart1_path:
                chart_files.append(chart1_path)
                logger.info(f"✅ Strong Momentum chart saved: {chart1_path}")

        if group2_codes:
            logger.info(f"\n📊 Generating charts for Potential Stocks Group...")
            chart2_path = plot_stock_charts(
                group2_codes,
                hist,
                output_filename=f"potential_stocks_{datetime.now().strftime('%Y%m%d')}.png"
            )
            if chart2_path:
                chart_files.append(chart2_path)
                logger.info(f"✅ Potential Stocks chart saved: {chart2_path}")

        # ===== Step 6: Save Results to CSV =====
        logger.info("\n📌 Step 6: Save Results to CSV")
        os.makedirs("output", exist_ok=True)
        csv_filename = f"output/stock_picks_{datetime.now().strftime('%Y%m%d')}.csv"
        picked.to_csv(csv_filename, index=False)
        logger.info(f"✅ Results saved to: {csv_filename}")

        # ===== Step 7: Generate HTML for GitHub Pages =====
        logger.info("\n📌 Step 7: Generate HTML for GitHub Pages")

        date_str = datetime.now().strftime('%Y-%m-%d')
        docs_dir = "docs"
        os.makedirs(docs_dir, exist_ok=True)

        # Copy chart images to docs directory
        chart1_filename = None
        chart2_filename = None

        if group1_codes and len(chart_files) > 0:
            chart1_src = chart_files[0]
            chart1_filename = f"strong_momentum_{datetime.now().strftime('%Y%m%d')}.png"
            chart1_dest = os.path.join(docs_dir, chart1_filename)
            shutil.copy2(chart1_src, chart1_dest)
            logger.info(f"📋 Copied chart to docs: {chart1_dest}")

        if group2_codes and len(chart_files) > 1:
            chart2_src = chart_files[1]
            chart2_filename = f"potential_stocks_{datetime.now().strftime('%Y%m%d')}.png"
            chart2_dest = os.path.join(docs_dir, chart2_filename)
            shutil.copy2(chart2_src, chart2_dest)
            logger.info(f"📋 Copied chart to docs: {chart2_dest}")

        # Generate daily HTML
        daily_html = generate_daily_html(
            picked,
            date_str,
            group1_codes,
            group2_codes,
            chart1_url=chart1_filename,
            chart2_url=chart2_filename,
            output_dir=docs_dir
        )
        logger.info(f"✅ Generated daily HTML: {daily_html}")

        # Load or create history index
        history_file = os.path.join(docs_dir, "history.json")
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history_data = json.load(f)
        else:
            history_data = []

        # Update history
        existing_entry = next((item for item in history_data if item['date'] == date_str), None)
        if existing_entry:
            existing_entry.update({
                'strong': len(group1_codes),
                'potential': len(group2_codes),
                'total': len(picked)
            })
        else:
            history_data.append({
                'date': date_str,
                'strong': len(group1_codes),
                'potential': len(group2_codes),
                'total': len(picked)
            })

        # Keep only last 30 days
        history_data = sorted(history_data, key=lambda x: x['date'], reverse=True)[:30]

        # Save history
        with open(history_file, 'w') as f:
            json.dump(history_data, f, indent=2)

        # Generate index HTML
        index_html = generate_index_html(history_data, output_dir=docs_dir)
        logger.info(f"✅ Generated index HTML: {index_html}")

        # ===== Summary =====
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()

        logger.info("\n" + "=" * 50)
        logger.info("✅ US Stocks Autobot Execution Complete")
        logger.info(f"⏱️  Total execution time: {elapsed:.2f} seconds")
        logger.info(f"📊 Total selected stocks: {len(picked)}")
        logger.info(f"📈 Strong Momentum: {len(group1_codes)} stocks")
        logger.info(f"👀 Potential Stocks: {len(group2_codes)} stocks")
        logger.info(f"🖼️  Charts generated: {len(chart_files)} files")
        logger.info(f"💾 Results saved to: {csv_filename}")
        logger.info(f"🌐 GitHub Pages files: {docs_dir}/")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"❌ Error occurred: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
