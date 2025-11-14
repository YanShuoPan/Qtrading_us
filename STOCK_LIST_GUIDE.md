# Stock List Management Guide

本指南說明如何管理和更新美股清單。

## 📋 三種股票清單來源

專案支援三種優先級的股票清單：

### 1️⃣ 環境變數（最高優先級）
臨時指定特定股票進行測試或運行。

```bash
# 設置環境變數
export US_STOCK_CODES="AAPL,MSFT,GOOGL,AMZN,TSLA"

# 運行程式
python main.py
```

### 2️⃣ JSON 文件（中等優先級）
使用動態更新的完整股票清單。

**文件位置**：`data/us_stock_list.json`

**優點**：
- 包含 11,000+ 美股
- 定期更新
- 來自 NASDAQ 官方數據

### 3️⃣ 硬編碼清單（最低優先級）
內建的 200+ 主要股票作為備選。

**文件位置**：`modules/stock_codes.py` 中的 `DEFAULT_US_STOCKS`

## 🔄 更新股票清單

### 從 NASDAQ 下載最新清單

```bash
python update_stock_list.py
```

**輸出文件**：
- `data/us_stock_list.json` - 過濾後的清單（11,475 股票）
- `data/us_stock_list_all.json` - 完整清單（11,480 股票）

**過濾條件**：
- 只包含字母符號（排除數字和特殊字符）
- 1-5 個字符長度
- 排除測試符號（如 TEST, ZZZZ）

### 按流動性篩選

如果 11,000+ 股票太多，可以篩選出流動性好的股票：

```bash
python filter_liquid_stocks.py
```

**輸出文件**：
- `data/liquid_stocks.json` - 包含交易量詳情
- `data/liquid_stocks_list.json` - 只含股票代碼

**篩選條件**：
- 平均每日交易量 >= 100萬股
- 基於最近 5 個交易日

**使用篩選後的清單**：

修改 `modules/stock_codes.py` 中的 `load_stock_list_from_json()` 函數：

```python
def load_stock_list_from_json(filepath='data/liquid_stocks_list.json'):  # 改這裡
    # ... rest of code
```

或在主程式中指定：

```python
from modules.stock_codes import load_stock_list_from_json
codes = load_stock_list_from_json('data/liquid_stocks_list.json')
```

## 📊 清單統計

### 完整清單（us_stock_list.json）
- **總數**：11,475 個股票
- **來源**：NASDAQ 官方數據
- **1 字元**：21 個（如 A, C, F）
- **2 字元**：274 個（如 AA, BA, GM）
- **3 字元**：2,719 個（如 AAPL, MSFT）
- **4 字元**：7,651 個（如 AMZN, GOOGL）
- **5 字元**：810 個（如 TSLA, NVDA）

### 流動性清單（需要運行 filter_liquid_stocks.py 生成）
- **條件**：平均日交易量 >= 100萬股
- **預估數量**：約 2,000-3,000 個股票
- **優點**：更適合技術分析和自動交易

## 🎯 建議用法

### 開發測試
使用環境變數指定少量股票：
```bash
export US_STOCK_CODES="AAPL,MSFT,GOOGL,AMZN,NVDA,TSLA,META,JPM,JNJ,V"
python main.py
```

### 生產環境
1. **方案 A**：使用流動性清單（推薦）
   - 運行 `filter_liquid_stocks.py` 生成清單
   - 約 2,000-3,000 支流動性好的股票
   - 更快的執行速度

2. **方案 B**：使用完整清單
   - 直接使用 `us_stock_list.json`
   - 11,475 支股票
   - 需要更長的執行時間

3. **方案 C**：使用硬編碼清單
   - 無需額外文件
   - 230 支主要股票
   - 最快的執行速度

## 🔧 自訂清單

### 創建自訂清單

1. **從完整清單篩選**：
```python
import json

# 讀取完整清單
with open('data/us_stock_list.json', 'r') as f:
    data = json.load(f)
    all_tickers = data['tickers']

# 篩選條件（例如：只要 3 字元的）
custom_tickers = [t for t in all_tickers if len(t) == 3]

# 儲存
custom_data = {
    'generated_at': '2025-11-14',
    'total_count': len(custom_tickers),
    'tickers': custom_tickers
}

with open('data/custom_stock_list.json', 'w') as f:
    json.dump(custom_data, f, indent=2)
```

2. **手動創建**：
```json
{
  "generated_at": "2025-11-14",
  "total_count": 10,
  "tickers": [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
    "NVDA", "TSLA", "JPM", "JNJ", "V"
  ]
}
```

### 使用自訂清單

修改 `modules/stock_codes.py`：
```python
def load_stock_list_from_json(filepath='data/custom_stock_list.json'):
    # ... rest of code
```

## 📅 定期更新

建議每月更新一次股票清單：

```bash
# 1. 更新完整清單
python update_stock_list.py

# 2. 篩選流動性股票
python filter_liquid_stocks.py

# 3. 提交更新
git add data/*.json
git commit -m "Update stock list - $(date +'%Y-%m')"
git push
```

## ⚠️ 注意事項

1. **API 限制**：
   - Yahoo Finance 有請求限制
   - 大量下載時建議分批處理
   - 使用 `filter_liquid_stocks.py` 時注意超時

2. **數據品質**：
   - 某些股票代碼可能已下市
   - 新上市股票可能缺少歷史數據
   - 建議使用流動性清單避免問題股票

3. **執行時間**：
   - 11,000+ 股票：需要 2-3 小時
   - 2,000-3,000 流動股票：需要 20-40 分鐘
   - 230 預設股票：需要 3-5 分鐘

4. **GitHub Actions 限制**：
   - Workflow 有 6 小時超時限制
   - 建議使用流動性清單或預設清單

## 🔍 查看當前使用的清單

運行測試腳本查看：
```bash
python -c "from modules.stock_codes import get_stock_codes; codes = get_stock_codes(); print(f'Total: {len(codes)}'); print(f'Source: JSON file' if len(codes) > 1000 else 'Source: Default list')"
```

---

**相關文件**：
- `update_stock_list.py` - 更新股票清單
- `filter_liquid_stocks.py` - 篩選流動性股票
- `modules/stock_codes.py` - 股票代碼管理模組
