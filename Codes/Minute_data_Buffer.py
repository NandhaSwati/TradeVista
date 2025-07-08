#!/usr/bin/python
import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Data'))
file_path = os.path.join(folder_path, "nifty50_symbol.csv")

symbols = pd.read_csv("D:/Arkalogi/Project/Data/nifty50_symbols.csv")
symbol_list = symbols['tradingsymbol'].tolist()
output_folder = "Project/Data/Minute_data"

start_date = datetime(2025, 6, 12)
end_date = start_date + timedelta(days=7)

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

    filename = f"{symbol}.csv"
    file_path = os.path.join(folder_path, filename)

    if os.path.exists(file_path):
        return

    data.to_csv(file_path, index=False)

def download_minute_data():
    for symbol in symbol_list:
        full_symbol = f"{symbol}.NS"

        for delta in range((end_date - start_date).days):
            day = start_date + timedelta(days=delta)
            next_day = day + timedelta(days=1)
            date_str = day.strftime("%Y-%m-%d")

            # Check if file already exists
            year = str(day.year)
            month = month_map[day.strftime("%m")]
            day_str = day.strftime("%d")
            path_check = os.path.join(output_folder, year, month, day_str, f"{symbol}.csv")
            if os.path.exists(path_check):
                continue

            try:
                ticker = yf.Ticker(full_symbol)
                data = ticker.history(start=day, end=next_day, interval='1m')
                if data.empty:
                    continue

                data.reset_index(inplace=True)
                data['Date'] = data['Datetime'].dt.date
                data['Time'] = data['Datetime'].dt.time
                df = data[['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume']]

                save_to_folder(df, symbol, date_str)

            except Exception as e:
                print(f"❌ Error downloading {symbol} on {date_str}: {e}")