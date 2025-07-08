#!/usr/bin/python
import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

symbols = pd.read_csv("D:/Arkalogi/Project/Data/nifty50_symbols.csv")
symbol_list = symbols['tradingsymbol'].tolist()
output_folder = "Project/Data/Day_data"

month_map = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
    "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
    "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
}

def save_to_folder(data, symbol, date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    year = str(date_obj.year)
    month = month_map[date_obj.strftime("%m")]
    day = date_obj.strftime("%d")

    folder_path = os.path.join(output_folder, year, month, day)
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, f"{symbol}.csv")
    data.to_csv(file_path, index=False)

def get_latest_saved_date(symbol):
    

    latest_date = None
    for root, _, files in os.walk(output_folder):
        for file in files:
            if file == f"{symbol}.csv":
                try:
                    df = pd.read_csv(os.path.join(root, file))
                    if not df.empty:
                        df['Date'] = pd.to_datetime(df['Date']).dt.date
                        max_date = df['Date'].max()
                        if latest_date is None or max_date > latest_date:
                            latest_date = max_date
                except:
                    continue
    return latest_date

def get_valid_end_date():
    curr_date = datetime.now().date()
    curr_time = datetime.now().time()
    closing_time = datetime.strptime("16:00:00", "%H:%M:%S").time()
    return curr_date - timedelta(days=1) if curr_time < closing_time else curr_date

def download_day_data():
    for symbol in symbol_list:
        print(f"\n🔍 Checking data for {symbol}...")
        full_symbol = f"{symbol}.NS"
        latest_saved = get_latest_saved_date(symbol)
        valid_end = get_valid_end_date()

        # If no data exists, download full 6 months
        if latest_saved is None:
            print("📁 No folder found — downloading last 6 months of data...")
            ticker = yf.Ticker(full_symbol)
            df = ticker.history(period="6mo", interval="1d", end=valid_end + timedelta(days=1))
        else:
            # If data already up to date
            if latest_saved >= valid_end:
                continue

            # Else download only missing days
            start_date = latest_saved + timedelta(days=1)
            print(f"📅 Downloading from {start_date} to {valid_end}")
            ticker = yf.Ticker(full_symbol)
            df = ticker.history(start=start_date, end=valid_end + timedelta(days=1), interval="1d")

        if df.empty:
            continue

        df.reset_index(inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.date

        new_rows = 0
        for i in range(len(df)):
            row = df.iloc[[i]].copy()
            row_date = row['Date'].values[0]
            row["Symbol"] = symbol
            date_str = pd.to_datetime(row_date).strftime("%Y-%m-%d")
            save_to_folder(row, symbol, date_str)
            new_rows += 1

        print(f"⬇️  Saved {new_rows} new day(s) for {symbol}")
