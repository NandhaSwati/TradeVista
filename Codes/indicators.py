from datetime import datetime, timedelta
import os
from flask import jsonify
import pandas as pd

#df = pd.read_csv("Task8/Data/sbin.csv")
Base_path = "D:/Arkalogi/Project/Data/Day_data"

def get_close_price(input_date, symbol, max_lookback=5):
    input_dt = datetime.strptime(input_date, "%Y-%m-%d")

    for i in range(max_lookback):
        try_date = input_dt - timedelta(days=i)
        try_date_str = try_date.strftime("%Y-%m-%d")
        year, month, day = try_date_str.split("-")
        month_name = datetime.strptime(month, "%m").strftime("%b")

        file_path = os.path.join(Base_path, year, month_name, day, f"{symbol}.csv")

        if not os.path.exists(file_path):
            print(f"[DEBUG] File not found: {file_path}")
            continue

        try:
            df = pd.read_csv(file_path)

            if 'Date' not in df.columns or 'Close' not in df.columns:
                print(f"[ERROR] 'Date' or 'Close' column missing in: {file_path}")
                continue

            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
            result = df[df['Date'] == try_date_str]

            if not result.empty:
                return float(result.iloc[0]['Close'])
        except Exception as e:
            print(f"Error reading file: {e}")
            continue

    print(f"No valid close price found for {symbol} on or before {input_date}")
    return 0


def EMA(symbol, date_str, w_size):
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    start_date =  date - timedelta(days= w_size * 2)
    current_date = start_date + timedelta(days=1)
    
    k = round(2/ (w_size + 1), 3)
    prev_ema = None
    last_valid_close = 0

    while current_date <= date:
        current_date_str = current_date.strftime("%Y-%m-%d")
        close_price = get_close_price(current_date_str, symbol)
        close_price = round(close_price, 2)

        if close_price == 0:
            current_date += timedelta(days=1)
            continue

        last_valid_close = close_price
        if prev_ema is None:
            prev_ema = close_price
        else:
            prev_ema = round((close_price * k) + prev_ema * (1-k), 2)
        
        current_date += timedelta(days=1)
    return {'Close' : last_valid_close, 'EMA': round(prev_ema, 4) if prev_ema is not None else 0}

def sma_calculation(symbol, date_str, number):
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    num = number
    sum = 0.0
    start_date = date - timedelta(days = num * 4)
    close_prices = []
    last_valid_close = 0

    while start_date <= date:
        start_date_str = start_date.strftime("%Y-%m-%d")
        close_price = get_close_price(start_date_str, symbol)
        if close_price != 0:
            last_valid_close = close_price
            if len(close_prices) < num:
                close_prices.append(close_price)
                sum += float(close_price)
        start_date += timedelta(days=1)

    sma = round((sum/num), 2) if num != 0 else 0

    return {"Close": round(last_valid_close, 2), "SMA" : round(sma,4)}

def StochRSI(symbol, date, rsi_length):
    data = RSI(symbol , date, rsi_length)
    if data.empty:
        return {"Close" : 0, "StochRSI" : 0}
    
    close_price = data.loc[len(data)-1, 'Close']
    curr_rsi = data.loc[len(data)-1, 'RSI']
    min_rsi = data['RSI'].min()
    max_rsi = data['RSI'].max()

    if max_rsi == min_rsi:
        stochRSI = 0
    else:
        stochRSI = (curr_rsi - min_rsi) / (max_rsi - min_rsi)

    return {"Close" : round(close_price, 2), 'StochRSI' : round(stochRSI, 4)}


def RSI(symbol, date_str, rsi_length):
    df = []
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    num = rsi_length * 2
    count = 0

    while count < num:
        current_date = date.strftime("%Y-%m-%d")
        close= get_close_price(current_date, symbol)
        if close == 0:
            date -= timedelta(days=1)
        else:
            df.append(close)
            date -= timedelta(days=1)
            count += 1

    data = pd.DataFrame(df, columns= ['Close'])
    data['Close'] = data["Close"].iloc[::-1].reset_index(drop= True)

    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_length).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window= rsi_length).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    data['RSI'] = round(rsi,4)

    return data

def widget(symbol, w_size):
    date = datetime.now().date()
    date_str = date.strftime("%Y-%m-%d")
    result = []

    result.append(sma_calculation(symbol, date_str, w_size))
    result.append(EMA(symbol, date_str, w_size))
    result.append(pd.Series(RSI(symbol, date_str, w_size).iloc[-1]))
    result.append(StochRSI(symbol, date_str, w_size))

    return result

"""
def widget(symbol, w_size):
    date = datetime.now().date()
    start_date = date - timedelta(days=15)

    sma_list = []
    ema_list = []
    rsi_list = []
    stochrsi_list = []

    while start_date < date:
        start_date_str = start_date.strftime("%Y-%m-%d")
        print(start_date_str)
        Close = get_close_price(start_date_str, symbol)
        sma = sma_calculation(symbol, start_date_str, w_size)
        ema = EMA(symbol, start_date_str, w_size)
        rsi = RSI(symbol, start_date_str, w_size)
        #stochRsi = StochRSI(symbol, start_date_str, w_size)

        sma_list.append({'Close' : sma['Close'], 'sma': sma['SMA']})
        ema_list.append({'Close' : ema['Close'], 'ema': ema['EMA']})
        rsi_list.append({'Close' : rsi['Close'], 'rsi': rsi['RSI']})
        #stochrsi_list.append({'Close' : stochRsi['Close'], 'sma': stochRsi['StochRSI']})
        start_date += timedelta(days=1)

    print(f"sma: {pd.Series(sma_list).tolist()},ema: {pd.Series(ema_list).tolist()},rsi: {pd.Series(rsi_list).tolist()},stochRSI: {pd.Series(stochrsi_list).tolist()}")
    return {
        "sma": pd.Series(sma_list).tolist(),
        "ema": pd.Series(ema_list).tolist(),
        "rsi": pd.Series(rsi_list).tolist(),
        
        #"stochRSI": pd.Series(stochrsi_list).tolist()
    }
"""      

if __name__ == '__main__':
    """
    ema =EMA("SBIN", "2025-06-11", 10)
    sma = sma_calculation("SBIN", "2025-06-11", 10)
    rsi = RSI("SBIN", "2025-06-11", 10)
    close_price = float(rsi['Close'].iloc[-1])
    value = float(rsi['RSI'].iloc[-1])
    stochRsi = StochRSI("SBIN", "2025-06-11", 10)

    print(ema)
    print(sma)
    print(f"Close: {close_price}, RSI: {value}")
    print(stochRsi)
    """
    #print(widget("SBIN", 6))
    print(StochRSI("SBIN","2025-06-02", 10))

