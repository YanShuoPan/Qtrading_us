# Quick Start Guide - 快速開始

## 📊 三種運行模式

### 1. 快速測試（10支股票）
最快，適合測試功能：
```bash
export US_STOCK_CODES="AAPL,MSFT,GOOGL,AMZN,NVDA,TSLA,META,JPM,JNJ,V"
python main.py
```
⏱️ 執行時間：~5 秒

### 2. 流動性股票清單（推薦）
使用交易量篩選後的股票（約 3,000 支）：

**首次運行**：
```bash
# 選擇選項 2: 測試 500 支（約 20 分鐘）
python filter_liquid_stocks_v2.py

# 之後使用篩選結果
python main.py
```

⏱️ 執行時間：~30-40 分鐘

### 3. 完整清單（11,475 支）
```bash
# 直接運行（會自動載入 data/us_stock_list.json）
python main.py
```
⏱️ 執行時間：~2-3 小時

## 🔧 常用命令

### 更新股票清單
```bash
# 從 NASDAQ 下載最新清單
python update_stock_list.py
```

### 篩選流動性股票
```bash
# V2 版本（推薦）- 更穩定
python filter_liquid_stocks_v2.py

# 互動式選擇:
# 1 = 測試 100 支 (~5 分鐘)
# 2 = 測試 500 支 (~20 分鐘)
# 3 = 處理全部 (~2-3 小時)
# 4 = 續傳之前的進度
```

### 測試設置
```bash
# 測試模組載入
python test_setup.py

# 快速測試（10支股票）
python test_quick.py
```

## 📁 重要文件

- `data/us_stock_list.json` - 完整股票清單（11,475 支）
- `data/liquid_stocks_list.json` - 流動性股票（篩選後）
- `data/us_stocks.sqlite` - 股價資料庫
- `docs/` - GitHub Pages 網頁文件
- `output/` - 本地輸出（CSV + 圖表）

## 🌐 查看結果

### 本地文件
- `output/stock_picks_YYYYMMDD.csv` - 每日選股結果
- `output/strong_momentum_YYYYMMDD.png` - 強勢股圖表
- `output/potential_stocks_YYYYMMDD.png` - 潛力股圖表

### GitHub Pages
網址：https://yansuopan.github.io/Qtrading_us/

## ⚙️ 配置選項

### 環境變數
創建 `.env` 文件：
```bash
# Debug 模式
DEBUG_MODE=false

# 最多選幾支股票
TOP_K=12

# 歷史資料天數
LOOKBACK_DAYS=120

# 自訂股票清單（會覆蓋 JSON 文件）
# US_STOCK_CODES=AAPL,MSFT,GOOGL
```

### 修改預設值
編輯 `modules/config.py`

## ❓ 常見問題

**Q: 執行太慢怎麼辦？**
A: 使用流動性股票清單或自訂小清單。

**Q: 如何只測試幾支股票？**
A: 使用環境變數 `US_STOCK_CODES`。

**Q: GitHub Actions 超時？**
A: 使用流動性清單（~3,000支）或預設清單（230支）。

**Q: 要多久更新一次股票清單？**
A: 每月一次即可，使用 `python update_stock_list.py`。

## 📚 詳細文檔

- [完整 README](README.md)
- [股票清單管理指南](STOCK_LIST_GUIDE.md)
- [GitHub Pages 設置指南](SETUP_GITHUB_PAGES.md)
- [專案總結](SUMMARY.md)

---

**需要幫助？** 查看 [GitHub Issues](https://github.com/YanShuoPan/Qtrading_us/issues)
