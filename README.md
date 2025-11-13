# US Stocks Autobot

Automated stock selection system for US equities using momentum-based technical analysis.

**🌐 Live Demo**: View the latest picks on [GitHub Pages](https://YOUR_USERNAME.github.io/us-stocks-autobot/)

## 🎯 Features

### 📊 Smart Stock Selection
- **Technical Indicator Analysis**: 20-day Moving Average (MA20) with slope calculation
- **Multiple Filter Criteria**:
  - Last 5 days open/close prices above MA20
  - MA20 slope < 2.0 (avoid overheated stocks)
  - Volatility < 8% (risk control)
  - Distance from MA20 within dynamic range
  - Minimum volume: 1M shares/day (10-day average)
  - Average high-low range > $0.50

### 🏷️ Dual Group Classification
- **🔥 Strong Momentum**: MA20 slope 0.8-2.0 (strong uptrend)
- **👀 Potential Stocks**: MA20 slope < 0.8 (potential opportunities)

### 📈 Visualization
- **Candlestick Charts**: 2×3 grid layout, up to 6 stocks per group
- **Technical Overlays**: MA20 moving average line
- **90-day History**: 3 months of price action for complete technical analysis
- **Professional Color Scheme**: Green for up days, red for down days

### 💾 Data Management
- **SQLite Database**: Local caching to avoid redundant downloads
- **Incremental Updates**: Only fetch new data when needed
- **CSV Export**: Daily stock picks saved to CSV for further analysis

### 🌐 GitHub Pages Integration
- **Automated Deployment**: Daily picks published to GitHub Pages
- **Historical Archive**: Last 30 days of picks with interactive charts
- **Responsive Design**: Mobile-friendly interface
- **Real-time Updates**: Automatically updated after each run

## 🚀 Quick Start

### Local Installation

```bash
# Clone or copy the project
cd us-stocks-autobot

# Install dependencies
pip install -r requirements.txt

# Run the program
python main.py
```

### GitHub Actions Setup (Automated Daily Picks)

1. **Fork or create a new repository** with this code

2. **Enable GitHub Pages**:
   - Go to repository **Settings** → **Pages**
   - Source: **GitHub Actions**
   - Save

3. **Enable Actions**:
   - Go to **Actions** tab
   - Click "I understand my workflows, go ahead and enable them"

4. **Run manually** (optional):
   - Go to **Actions** → **Daily Stock Picks**
   - Click **Run workflow**
   - Your picks will be generated and deployed to GitHub Pages

5. **View your results**:
   - Visit `https://YOUR_USERNAME.github.io/REPO_NAME/`
   - Bookmark this page for daily updates!

**Automatic Schedule**: The workflow runs automatically every day at **9:30 PM EST** (after US market close), Tuesday through Saturday (covering Monday-Friday trading days).

### Configuration

Create a `.env` file (optional):

```bash
# Debug mode (detailed logging)
DEBUG_MODE=false

# Maximum stocks to select
TOP_K=12

# Historical data lookback period (days)
LOOKBACK_DAYS=120

# Custom stock list (comma-separated, optional)
# If not set, uses built-in S&P 100 + major stocks list
US_STOCK_CODES=AAPL,MSFT,GOOGL,AMZN,META,NVDA,TSLA
```

## 📊 Supported Stocks

Default list includes **200+ major US stocks**:
- **Technology**: AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, etc.
- **Healthcare**: UNH, JNJ, LLY, ABBV, MRK, TMO, ABT, etc.
- **Financials**: BRK.B, JPM, V, MA, BAC, WFC, GS, MS, etc.
- **Consumer**: WMT, HD, MCD, NKE, SBUX, COST, KO, PEP, etc.
- **Energy**: XOM, CVX, COP, SLB, EOG, MPC, etc.
- **Industrials**: BA, HON, UNP, RTX, UPS, CAT, LMT, GE, etc.
- **And more across all major sectors**

## 📁 Project Structure

```
us-stocks-autobot/
├── main.py                     # Main program
├── modules/                    # Modular architecture
│   ├── __init__.py            # Package initialization
│   ├── config.py              # Configuration management
│   ├── logger.py              # Logging system
│   ├── database.py            # Database operations
│   ├── stock_codes.py         # Stock symbol management
│   ├── stock_data.py          # Price data processing & selection strategy
│   ├── visualization.py       # Candlestick chart generation
│   └── html_generator.py      # GitHub Pages HTML generator
├── data/                      # Database files
│   └── us_stocks.sqlite       # Stock price history
├── output/                    # Generated files
│   ├── stock_picks_YYYYMMDD.csv          # Daily picks CSV
│   ├── strong_momentum_YYYYMMDD.png      # Strong momentum charts
│   └── potential_stocks_YYYYMMDD.png     # Potential stocks charts
├── docs/                      # GitHub Pages files (auto-generated)
│   ├── index.html             # Historical picks index
│   ├── YYYY-MM-DD.html        # Daily picks page
│   ├── *.png                  # Chart images
│   └── history.json           # Historical data (30 days)
├── .github/
│   └── workflows/
│       └── daily-picks.yml    # GitHub Actions automation
├── requirements.txt           # Python dependencies
└── README.md                 # Project documentation
```

## 🔬 Technical Details

### Core Technology Stack
- **Language**: Python 3.8+
- **Data Source**: Yahoo Finance API (yfinance)
- **Database**: SQLite (local caching)
- **Visualization**: matplotlib with custom candlestick function

### Modular Architecture
- **config.py**: Centralized environment variable management
- **logger.py**: Unified logging system
- **database.py**: Stock price data operations
- **stock_codes.py**: 200+ US stock symbols and names
- **stock_data.py**: Price download & momentum selection strategy
- **visualization.py**: Candlestick chart rendering
- **html_generator.py**: GitHub Pages HTML generation

## 📈 Selection Algorithm

### Filter Criteria
1. **Trend Check**: Last 5 days open/close average above MA20
2. **Slope Control**: MA20 slope < 2.0 (avoid excessive momentum)
3. **Volatility Limit**: 5-day price std dev < 8%
4. **Distance Control**: Price-to-MA20 distance within dynamic range
5. **Liquidity**: Average volume > 1M shares (last 10 days)
6. **Price Action**: Average high-low spread > $0.50

### Grouping Logic
- **Strong Momentum Group**: Slope ∈ [0.8, 2), representing steady uptrend
- **Potential Stocks Group**: Slope < 0.8, representing early-stage opportunities

### Optimization
When group has > 6 stocks:
1. Exclude stocks at 5-day low close price
2. Select 6 stocks closest to MA20

## 🛠️ Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run with debug mode
DEBUG_MODE=true python main.py

# Check debug logs
cat debug.log
```

### Customization

You can customize the stock selection by:
1. Editing `modules/stock_codes.py` to change stock universe
2. Adjusting filter parameters in `modules/stock_data.py`
3. Modifying chart layout in `modules/visualization.py`

## 📝 Output Examples

### Console Output
```
🚀 US Stocks Autobot Execution Started
📌 Step 1: Initialize Database
📌 Step 2: Download Stock Data
📌 Step 3: Load Data and Select Stocks
📌 Step 4: Stock Selection Results

🔥 Strong Momentum Group (MA20 slope >= 0.8):
   Total: 4 stocks
   - AAPL Apple Inc: Close=$175.43, MA20=$172.15, Slope=0.912, Vol=2.34%
   - MSFT Microsoft: Close=$378.91, MA20=$375.20, Slope=0.856, Vol=2.87%

👀 Potential Stocks Group (MA20 slope < 0.8):
   Total: 3 stocks
   - GOOGL Alphabet A: Close=$142.35, MA20=$140.89, Slope=0.623, Vol=3.12%
```

### Generated Files
- `output/stock_picks_20250113.csv` - Detailed stock metrics
- `output/strong_momentum_20250113.png` - Charts for strong stocks
- `output/potential_stocks_20250113.png` - Charts for potential stocks

## ⚠️ Disclaimer

This project is for educational and research purposes only. It does not constitute investment advice. Trading involves risk. Please conduct your own due diligence.

## 📄 License

MIT License - Feel free to use and modify for your own purposes.

---

**Note**: This is a US stocks adaptation of the Taiwan stocks autobot, modified for US market characteristics and without LINE messaging integration.
