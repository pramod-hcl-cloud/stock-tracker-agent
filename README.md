# AlphaQuant Intelligence Terminal | Multi-Currency Portfolio

A sleek, institutional-grade dark-mode financial terminal built with **Streamlit**, **Plotly**, and **yfinance**, featuring automated quantitative indicators and a simulated **Vertex AI Quantitative Agent Research Summary**.

---

## 🌐 Currency Regimes by Asset

| Asset Name | Primary Ticker & Exchange | Active Currency | Currency Framework |
| :--- | :--- | :--- | :--- |
| **HDFCBANK** | `HDFCBANK.NS` (NSE India) | **`₹ INR`** | **Native Indian Rupee** (No FX conversion) |
| **HCLTECH** | `HCLTECH.NS` (NSE India) | **`₹ INR`** | **Native Indian Rupee** (No FX conversion) |
| **Shopify** | `SHOP.TO` (TSX Canada) | **`$ CAD`** | **Native Canadian Dollar** (TSX Domestic) |
| **Berkshire Hathaway** | `BRK-B` (NYSE USA) | **`$ CAD`** | **CAD Hedged** via live USD/CAD (`USDCAD=X`) |
| **AAPL** | `AAPL` (NASDAQ USA) | **`$ CAD`** | **CAD Hedged** via live USD/CAD (`USDCAD=X`) |
| **United Healthcare** | `UNH` (NYSE USA) | **`$ CAD`** | **CAD Hedged** via live USD/CAD (`USDCAD=X`) |

---

## 🚀 Key Dashboard Features

1. **Interactive Sidebar**:
   - Stock selector configured with the 6 assets with clear currency tags (`[INR ₹]`, `[CAD $]`, `[CAD Hedged $]`).
   - Timeframe selector (defaults to **3 Months** / `period="3m"` / `period="3mo"`).
   - "🚀 Run Agentic Analysis" trigger button.
   - Custom ticker override option.

2. **Unified Vertical Plotly Layout (3 Linked Subplots Sharing X-Axis)**:
   - **Panel 1 (Top)**: Candlestick price chart denominated in the asset's active currency (`₹ INR` for India, `$ CAD` for others) overlaid with **EMA 12** and **EMA 26**, plus **Volume bars** on secondary Y-axis (anchored to bottom 25%).
   - **Panel 2 (Middle)**: **RSI (14-period)** indicator with dotted horizontal boundary lines at **30 (oversold)** and **70 (overbought)**, 50 midline, and shaded neutral momentum corridors.
   - **Panel 3 (Bottom)**: **MACD Line**, **Signal Line**, and a color-coded **Histogram** in the asset's active currency (Green `#00F5A0` for positive momentum, Red `#FF3B30` for negative).
   - **Synchronized Crosshairs**: Unified hover crosshair (`hovermode="x unified"`) across all three panels.

3. **🤖 Vertex AI Agent Research Summary**:
   - Distinct, glowing glassmorphic card container at the bottom.
   - Formulates institutional quantitative research reports with asset-specific currency formatting:
     - Exact active crossover detection (lookback session counter).
     - MACD zero-line expansion vs contraction status.
     - RSI oscillator health and momentum exhaustion warning levels.
     - Price vs EMA12 vs EMA26 stacking structure.
     - Volume confirmation vs 20-day moving average.
     - Strategic quantitative stance, model confidence rating, support/resistance levels, and model invalidation stop-loss.

---

## 💻 Quick Start & Local Execution

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Run automated test suite
python test_app.py

# 3. Launch dashboard
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.
