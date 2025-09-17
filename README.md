# 📈 Binance Futures Cross Margin Calculator

An interactive **Streamlit web app** to calculate **liquidation prices, PnL (Profit & Loss), and visualize cross margin futures positions** in real-time using **live Binance API prices**.

This tool simulates how Binance actually handles **cross margin liquidation**, including position grouping, maintenance margin, wallet balance, and live market conditions.

---

## 🚀 Features

* **Live Prices from Binance API**

  * Fetches **Futures prices** with fallback to **Spot prices** if needed.
  * Automatic and manual refresh options.
  * Fallback default prices for offline/demo mode.

* **Cross Margin Position Management**

  * Add **LONG** or **SHORT** positions across multiple cryptocurrencies.
  * Supports custom entry prices, leverage, position size, and maintenance margin rates.
  * Handles multiple positions per symbol, grouped like Binance does.

* **PnL & Liquidation Analysis**

  * Real-time calculation of **PnL** for all positions.
  * Wallet balance and margin ratio tracking.
  * Cross margin liquidation prices with detailed explanations.
  * Liquidation risk ranking & warnings.

* **Interactive Visualizations**

  * **PnL by Position** (bar chart).
  * **Price Sensitivity Analysis** (PnL vs price range).
  * **Liquidation Analysis** (grouped position breakdown).
  * Cross margin interaction effects between positions.

* **Debugging & Connectivity Checks**

  * Built-in tools in sidebar to check API connectivity and caching.
  * Auto-refresh option with 30s intervals.

---

## 🛠️ Installation

1. Clone this repo:

```bash
git clone https://github.com/yourusername/binance-cross-margin-calculator.git
cd binance-cross-margin-calculator
```

2. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

**requirements.txt**

```
streamlit
pandas
numpy
plotly
requests
urllib3
```

---

## ▶️ Usage

Run the app with:

```bash
streamlit run app.py
```

Open your browser at: [http://localhost:8501](http://localhost:8501)

---

## 📊 Example Workflow

1. Start with a wallet balance (default: **1000 USDT**).
2. Add positions (e.g., **BTCUSDT LONG 10x with \$500 size**).
3. Monitor **PnL, margin usage, and liquidation risk**.
4. Explore **PnL charts** and **price sensitivity analysis**.
5. Add multiple positions to see how they **interact under cross margin**.

---

## ⚠️ Disclaimer

This calculator is for **educational purposes only**.
It does **not guarantee accuracy** and should **not be used for real trading decisions**.
Always verify calculations independently before trading futures.

---

## 📌 Roadmap / Future Improvements

* ✅ Support more Binance symbols automatically from API
* ✅ Add auto-refresh toggle
* 🔲 Historical PnL tracking
* 🔲 Multi-wallet simulations
* 🔲 Integration with trading bots

