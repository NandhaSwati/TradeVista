from datetime import datetime, timedelta
import os
import pandas as pd

def get_close_price(base_dir, input_date, symbol):
    try:
        # Parse date
        year, month, day = input_date.split("-")
        month_name = datetime.strptime(month, "%m").strftime("%b")

        # Build file path
        file_path = os.path.join(base_dir, "History_Data", year, month_name, day, f"{symbol}.csv")

        # Check file existence
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return 0

        # Read CSV and clean headers
        df = pd.read_csv(file_path)
        df.columns = [col.split('.')[-1] for col in df.columns]  # Clean headers like Symbol.NS

        # Filter row with matching date
        result = df[df['Date'] == input_date]

        if not result.empty:
            return result.iloc[0]['Close']
        else:
            print("Date not found in the file.")
            return 0

    except Exception as e:
        print("Error:", e)
        return 0 

def sma_calculation(number, date_str, symbol):
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    num = number
    sum = 0.0
    start_date = date - timedelta(days = num * 4)
    close_prices = []
    while start_date <= date:
        date_str = start_date.strftime("%Y-%m-%d")
        close_price = get_close_price("Task6", date_str, symbol)
        if close_price != 0 and len(close_prices) < num:
            close_prices.append(close_price)
            sum += float(close_price)
        start_date += timedelta(days=1)
    sma = round((sum/num), 2)
    close_price = round(float(close_prices[-1]), 2)

    return {"sma": sma, "Close_price" : close_price}

if __name__ == '__main__':
    result = sma_calculation("2025-05-27", "SBIN")
    for key, value in result.items():
        print(f"{key} : {value}")
        