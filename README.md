# TradeVista 📈

**TradeVista** is a web-based stock market analysis tool that provides interactive visualizations, technical indicator-based recommendations, profit & loss tracking, and company insights. Built using **Flask (Python)** for the backend and **HTML, CSS, JavaScript** for the frontend, it integrates real-time stock data via **Yahoo Finance (yfinance)**.

---

## 🔧 Technologies Used

### 📌 Backend:
- **Flask** (v3.1.1): Lightweight web framework
- **Pandas** (v2.2.2): Data manipulation and analysis
- **yfinance** (v0.2.65): Fetching stock market data
- **Pydantic** (v2.11.7): Data validation (if applicable)

### 🎨 Frontend:
- **HTML/CSS/JavaScript**
- **Chart.js / Plotly / Gauge.js** (presumed for charts)

---

## 🧠 Features & Services

### 📊 Homepage:
- **Line Chart**: 1-year data of major indices like NIFTY 50, BANK NIFTY, and SENSEX.
- **Dynamic Range Charts**: High/Low values for intervals (1 Day, 1 Week, 1 Month, 6 Months, 1 Year) — updated on button click.

### 🔎 Services:

#### 1. **Company Insight**
- Input: Company Symbol, Date & Window size for SMA indicator
- Output: Date, Company name, Close Price, SMA value & Recommendation

#### 2. **Market Insight**
- Input: Date & Window size for SMA indicator
- Output: Symbol for each company, Close Price, SMA & Recommendation for all 50 companies in NIFTY 50.

#### 3. **Profit and Loss Calculator**
- Input: Entry/Exit Date , Entry/Exit time, Position(long or short) & Comapany symbol
- Output: Date, Entry Close Price, Exit Close Price and Pnl value in the one table for the date in range of Entry to Exit date.
- **Bar Chart**: P&L visualization

#### 4. **Technical Indicators**
- Input: Company symbol, Date & Indicators
- Select Indicator: SMA, EMA, RSI, Stochastic RSI then enter the Window size
- Shows: Date, Symbol, Indicator, Window Size, Close price, Indicator value, Action in the form of table.
- **Persistent Table**: Stores indicator values until user deletes a row.

#### 5. **Widgets (Gauge Chart Recommendation)**
- Input: Company Symbol & Window size
- Output: Gauge Chart showing consensus recommendation using all 4 indicators.

#### 6. **Theme Toggle**
- Dark/Light mode switcher via navigation bar

---

## 🗃️ Project Structure

```bash
TradeVista/
├── Data/                  # CSS, JS, images
├── static/                # CSS, JS, images
├── templates/             # HTML pages (Jinja2)
├── Codes/main.py          # Main Flask application
├── requirements.txt       # Dependencies
└── README.md              # Project overview
```
---
### 🔄 Auto Data Update
- Uses **yfinance** to fetch daily stock data.
- Auto-updates every time the backend is started.

### 🚀 How to Run the Project
- Clone the project
```bash
git clone https://github.com/yourusername/TradeVista.git
cd TradeVista
```
- Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```
- Install dependencies
```bash
pip install -r requirements.txt
```
- Run Flask server
```bash
cd Codes
python main.py
```
