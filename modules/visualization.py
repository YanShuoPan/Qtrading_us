"""
Visualization module - Plot stock candlestick charts
"""
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from .stock_codes import get_stock_name
from .config import DEBUG_MODE, OUTPUT_DIR
from .logger import get_logger

logger = get_logger(__name__)


def plot_candlestick(ax, stock_data):
    """
    Plot standard candlestick chart on specified ax

    Args:
        ax: matplotlib axes object
        stock_data: Stock data DataFrame (index should be 0, 1, 2, ...)
    """
    logger.info(f"plot_candlestick input data: records={len(stock_data)}, index range={stock_data.index.min()}-{stock_data.index.max()}")

    for idx, row in stock_data.iterrows():
        date_num = idx
        open_price = row['open']
        high_price = row['high']
        low_price = row['low']
        close_price = row['close']

        # Green for up, Red for down (US convention)
        is_rise = close_price >= open_price
        body_color = '#27AE60' if is_rise else '#E74C3C'  # Green up, Red down
        line_color = body_color

        # Draw high-low line
        ax.plot([date_num, date_num], [low_price, high_price],
                color=line_color, linewidth=1, solid_capstyle='round')

        # Draw candlestick body (rectangle)
        body_height = abs(close_price - open_price)
        body_bottom = min(open_price, close_price)

        if body_height < 0.001:  # Doji (open = close)
            ax.plot([date_num - 0.3, date_num + 0.3], [close_price, close_price],
                   color=line_color, linewidth=1.5)
        else:
            # Draw body rectangle
            rect = Rectangle((date_num - 0.3, body_bottom), 0.6, body_height,
                           facecolor=body_color, edgecolor=line_color,
                           linewidth=0.8, alpha=0.9)
            ax.add_patch(rect)


def plot_stock_charts(codes: list, prices: pd.DataFrame, output_filename: str = None) -> str:
    """
    Plot up to 6 stocks candlestick charts (2x3 subplots)

    Args:
        codes: List of stock ticker symbols
        prices: Stock price DataFrame
        output_filename: Output filename (optional)

    Returns:
        str: Chart file path
    """
    logger.info(f'Starting chart generation, stock codes: {codes}')
    logger.info(f'Total price records: {len(prices)}')

    # Diagnostic: Check data range
    if not prices.empty and 'date' in prices.columns:
        logger.info(f'Price data date range: {prices["date"].min()} ~ {prices["date"].max()}')
        logger.info(f'Price data unique dates: {prices["date"].nunique()}')

    codes = codes[:6]
    n_stocks = len(codes)
    if n_stocks == 0:
        logger.warning("No stock codes to plot")
        return None

    # Font settings (cross-platform)
    fonts = ['DejaVu Sans', 'Arial', 'Microsoft JhengHei', 'SimHei', 'WenQuanYi Zen Hei']
    plt.rcParams['font.sans-serif'] = fonts
    plt.rcParams['axes.unicode_minus'] = False

    if DEBUG_MODE:
        logger.debug(f"matplotlib backend: {matplotlib.get_backend()}")
        logger.debug(f"Font order: {fonts}")

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()

    for i, code in enumerate(codes):
        stock_data = prices[prices["code"] == code].sort_values("date").tail(90)

        logger.info(f'Stock {code}: original records = {len(prices[prices["code"] == code])}, after tail(90) = {len(stock_data)}')
        if not stock_data.empty and 'date' in stock_data.columns:
            logger.info(f'Stock {code}: date range = {stock_data["date"].min()} ~ {stock_data["date"].max()}')
            logger.info(f'Stock {code}: unique dates = {stock_data["date"].nunique()}')

        if stock_data.empty or len(stock_data) < 20:
            stock_name = get_stock_name(code)
            axes[i].text(0.5, 0.5, f"{code} {stock_name}\nInsufficient Data",
                        ha='center', va='center', fontsize=14)
            axes[i].set_xticks([])
            axes[i].set_yticks([])
            continue

        stock_data = stock_data.copy().reset_index(drop=True)
        logger.info(f'Stock {code}: after reset_index() index range = {stock_data.index.min()}-{stock_data.index.max()}')
        stock_data["ma20"] = stock_data["close"].rolling(20, min_periods=20).mean()

        ax = axes[i]
        plot_candlestick(ax, stock_data)

        # Plot MA20
        valid_ma20 = stock_data[stock_data["ma20"].notna()]
        if not valid_ma20.empty:
            logger.info(f'Stock {code}: valid_ma20 index range = {valid_ma20.index.min()}-{valid_ma20.index.max()}')
            ma20_indices = valid_ma20.index - stock_data.index[0]
            logger.info(f'Stock {code}: ma20_indices range = {ma20_indices.min()}-{ma20_indices.max()}')
            ax.plot(ma20_indices, valid_ma20["ma20"], label="MA20",
                   linewidth=2, linestyle="--", alpha=0.7, color='#2E86DE')

        stock_name = get_stock_name(code)
        ax.set_title(f"{code} {stock_name}", fontsize=14, fontweight='bold', pad=10)
        ax.legend(fontsize=9, loc='upper left')
        ax.grid(True, alpha=0.3, linestyle='--')

        # Set X-axis date labels
        date_labels = stock_data["date"].dt.strftime('%m/%d').tolist()
        step = max(1, len(date_labels) // 6)
        tick_positions = list(range(0, len(date_labels), step))
        tick_labels = [date_labels[i] for i in tick_positions]
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=45, fontsize=9)
        ax.tick_params(axis='y', labelsize=9)

    # Remove extra subplots
    for i in range(n_stocks, 6):
        fig.delaxes(axes[i])

    plt.tight_layout()

    # Save chart to output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if output_filename is None:
        from datetime import datetime
        output_filename = f"stock_charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close()

    logger.info(f"✅ Chart generated: {output_path}")
    return output_path
