# US Stocks Autobot - 完整專案總結

## ✅ 專案完成狀態

已成功創建完整的美股自動選股系統，包含 GitHub Pages 網頁展示功能！

## 📁 專案結構總覽

```
us-stocks-autobot/
├── 📄 main.py                          # 主程式（含 HTML 生成）
├── 📁 modules/                         # 核心模組
│   ├── __init__.py                    # 套件初始化
│   ├── config.py                      # 配置管理
│   ├── logger.py                      # 日誌系統
│   ├── database.py                    # SQLite 資料庫操作
│   ├── stock_codes.py                 # 200+ 美股代碼
│   ├── stock_data.py                  # 股價數據與選股策略
│   ├── visualization.py               # K線圖生成
│   └── html_generator.py              # 🆕 GitHub Pages HTML 生成器
├── 📁 .github/workflows/
│   └── daily-picks.yml                # 🆕 GitHub Actions 自動化
├── 📁 docs/                           # 🆕 GitHub Pages 檔案（自動生成）
│   ├── .nojekyll                      # GitHub Pages 配置
│   └── README.md                      # docs 說明
├── 📁 data/                           # 資料庫目錄（自動生成）
├── 📁 output/                         # 輸出目錄（自動生成）
├── 📄 requirements.txt                # Python 依賴
├── 📄 README.md                       # 專案說明
├── 📄 SETUP_GITHUB_PAGES.md          # 🆕 GitHub Pages 設置指南
├── 📄 test_setup.py                   # 設置測試腳本
├── 📄 .env.example                    # 環境變數範例
└── 📄 .gitignore                      # Git 忽略文件
```

## 🎯 主要功能

### 1. 自動選股系統
- ✅ 支援 200+ 美股（含 S&P 100 成分股）
- ✅ MA20 移動平均線技術分析
- ✅ 雙組分類（強勢動能 vs 潛力股票）
- ✅ 多重過濾條件（成交量、波動率、斜率）

### 2. 視覺化輸出
- ✅ K線圖自動生成（綠漲紅跌，美股習慣）
- ✅ 2×3 網格佈局
- ✅ MA20 技術指標線
- ✅ 90天歷史資料

### 3. 數據管理
- ✅ SQLite 本地快取
- ✅ 增量更新機制
- ✅ CSV 格式輸出

### 4. 🆕 GitHub Pages 整合
- ✅ 自動生成精美網頁
- ✅ 歷史資料展示（30天）
- ✅ 響應式設計（手機友好）
- ✅ 互動式圖表展示

### 5. 🆕 GitHub Actions 自動化
- ✅ 每日自動執行（美股收盤後）
- ✅ 自動部署到 GitHub Pages
- ✅ 支援手動觸發
- ✅ 執行日誌和錯誤追蹤

## 🚀 使用方式

### 本地運行

```bash
# 安裝依賴
pip install -r requirements.txt

# 執行程式
python main.py
```

### GitHub Pages 部署

詳見 [SETUP_GITHUB_PAGES.md](SETUP_GITHUB_PAGES.md)

**快速步驟**：
1. 創建 GitHub 倉庫
2. 推送代碼
3. 啟用 GitHub Pages (Source: GitHub Actions)
4. 啟用 GitHub Actions
5. 手動運行 workflow 或等待自動執行
6. 訪問 `https://YOUR_USERNAME.github.io/REPO_NAME/`

## 📊 輸出文件

### 本地文件（output/）
- `stock_picks_YYYYMMDD.csv` - 每日選股數據
- `strong_momentum_YYYYMMDD.png` - 強勢股票圖表
- `potential_stocks_YYYYMMDD.png` - 潛力股票圖表

### GitHub Pages 文件（docs/）
- `index.html` - 首頁（歷史列表）
- `YYYY-MM-DD.html` - 每日詳情頁
- `*.png` - 圖表圖片
- `history.json` - 歷史數據（最近30天）

## 🔧 技術細節

### 與台股版本的主要差異

| 項目 | 台股版本 | 美股版本 |
|------|---------|---------|
| 股票數量 | 300支台股 | 200+美股 |
| 代碼格式 | 需加 .TW 後綴 | 無後綴 |
| 成交量門檻 | 1000張 | 100萬股 |
| 波動率限制 | 3% | 8% |
| 斜率範圍 | < 1.0 | < 2.0 |
| 價格差異 | > 1元 | > $0.5 |
| K線顏色 | 紅漲綠跌 | 綠漲紅跌 |
| LINE 推播 | ✅ 支援 | ❌ 移除 |
| Google Drive | ✅ 支援 | ❌ 移除 |
| GitHub Pages | ✅ 支援 | ✅ 支援 |

### 核心模組說明

1. **config.py** - 環境變數管理
   - DEBUG_MODE, TOP_K, LOOKBACK_DAYS

2. **database.py** - SQLite 操作
   - 股價數據存儲
   - 增量更新

3. **stock_codes.py** - 股票代碼管理
   - 200+ 美股清單
   - 股票名稱對照

4. **stock_data.py** - 選股策略
   - 動能篩選算法
   - 雙組分類邏輯

5. **visualization.py** - 圖表生成
   - K線圖繪製
   - MA20 指標

6. **html_generator.py** - 網頁生成
   - 每日詳情頁
   - 歷史索引頁

## 📅 自動執行時間

- **時區**: 美東時間（EST）
- **時間**: 晚上 9:30 PM（美股收盤後）
- **星期**: 週二到週六（對應週一到週五交易日）
- **UTC 時間**: 次日凌晨 2:30 AM

## 🎨 網頁設計特色

- 🎨 漸層紫色主題
- 📱 響應式設計（手機、平板、電腦）
- 🖼️ 卡片式佈局
- 🎯 清晰的視覺層次
- ⚡ 快速載入
- 🔍 SEO 友好

## 🔐 安全性

- ✅ 無敏感資料（無 API key 需求）
- ✅ 公開數據源（Yahoo Finance）
- ✅ 開源代碼
- ✅ 無需身份驗證

## ⚠️ 免責聲明

本專案僅供學習和研究使用，不構成任何投資建議。
投資有風險，請謹慎評估。

## 📝 後續擴展建議

1. **技術指標**：
   - 增加 RSI、MACD 等指標
   - 支援多種技術分析策略

2. **回測功能**：
   - 歷史績效分析
   - 策略優化

3. **通知功能**：
   - Email 通知
   - Telegram Bot
   - Discord Webhook

4. **數據分析**：
   - 選股成功率統計
   - 收益率追蹤

5. **用戶界面**：
   - 互動式篩選
   - 自定義參數調整

## 🎉 總結

現在你有一個完整的美股自動選股系統，包含：

✅ **本地執行** - 隨時可以在電腦上運行
✅ **自動化** - GitHub Actions 每日自動執行
✅ **網頁展示** - GitHub Pages 精美網頁
✅ **歷史追蹤** - 30天歷史資料
✅ **開源免費** - 完全免費，無需任何 API key

**下一步**：
1. 閱讀 [SETUP_GITHUB_PAGES.md](SETUP_GITHUB_PAGES.md)
2. 部署到 GitHub
3. 享受每日自動選股！

---

Made with ❤️ for US Stock Market
