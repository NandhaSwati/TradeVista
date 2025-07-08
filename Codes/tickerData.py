from datetime import datetime, timedelta
import os
import pandas as pd
import yfinance as yf

# Month mapping for folder naming
month_map = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
    "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
    "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
}

# Save a specific day's minute data to folder
def save_to_folder(data, symbol, date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    year = str(date_obj.year)
    month = month_map[date_obj.strftime("%m")]
    day = date_obj.strftime("%d")

    folder_path = os.path.join("D:/Arkalogi/Project/Data/Ticker_Minute_data", year, month, day)
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, f"{symbol}.csv")

    if os.path.exists(file_path):
        print(f"[SKIP] Minute data already exists for {symbol} on {date_str}")
        return

    data.to_csv(file_path, index=False)
    print(f"[SAVED] Minute data for {symbol} on {date_str}")

# Append and update data for 1-day interval
def download_ticker_day_data(symbol):
    file_path = f"D:/Arkalogi/Project/Data/Ticker_data/{symbol}.csv"
    today = datetime.now().date()

    if not os.path.exists(file_path):
        print(f"[INFO] Downloading new daily data for {symbol}")
        tick = yf.Ticker(symbol)
        data = tick.history(period='2y', interval='1d')
        data.index = data.index.date
        data.index.name = 'Date'
        data.to_csv(file_path, index=True)
    else:
        print(f"[INFO] Updating daily data for {symbol}")
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d').dt.date
        df = df.dropna(subset=['Date'])
        if not df.empty:
            last_date = df['Date'].iloc[-1]
        else:
            last_date = None
        # Only update if today's data is missing
        if last_date is not None and last_date < today:
            tick = yf.Ticker(symbol)
            new_data = tick.history(start=last_date + timedelta(days=1), end=today + timedelta(days=1), interval='1d')
            if not new_data.empty:
                new_data.index = new_data.index.date
                new_data.reset_index(inplace=True)
                new_data.rename(columns={"index": "Date"}, inplace=True)
                combined = pd.concat([df, new_data], ignore_index=True)
                combined.to_csv(file_path, index=False)
                print(f"[UPDATED] Daily data for {symbol}")
            else:
                print(f"[NO DATA] No new daily data for {symbol}")
        else:
            print(f"[UP-TO-DATE] Daily data for {symbol}")

# Download and store 1-minute interval data if today's folder does not exist
def download_minute_data_if_missing(symbol):
    today = datetime.now().date()
    year = str(today.year)
    month = month_map[today.strftime("%m")]
    day = today.strftime("%d")
    folder_path = os.path.join("D:/Arkalogi/Project/Data/Ticker_Minute_data", year, month, day)
    file_path = os.path.join(folder_path, f"{symbol}.csv")

    if not os.path.exists(file_path):
        print(f"[INFO] Minute data missing for {symbol}, downloading...")
        os.makedirs(folder_path, exist_ok=True)

        tick = yf.Ticker(symbol)
        data = tick.history(start=today - timedelta(days=7), end=today + timedelta(days=1), interval='1m')
        
        if not data.empty:
            data.reset_index(inplace=True)
            data['Date'] = data['Datetime'].dt.date
            data['Time'] = data['Datetime'].dt.time
            df = data[['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume']]

            for date, group in df.groupby("Date"):
                date_str = pd.to_datetime(date).strftime("%Y-%m-%d")
                save_to_folder(group, symbol, date_str)
        else:
            print(f"[NO DATA] No minute data for {symbol}")
    else:
        print(f"[UP-TO-DATE] Minute data already exists for {symbol}")
