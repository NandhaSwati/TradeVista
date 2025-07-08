from flask import Flask, jsonify, render_template, request, redirect, url_for
import pandas as pd
from datetime import datetime, time, timedelta, date
import os
from sma_calclutator import *
from tickerData import *
from Minute_data_Buffer import download_minute_data
from Day_data_Buffer import download_day_data

from pydantic import BaseModel,field_validator, model_validator
from indicators import *


# Get absolute paths for template and static folders
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if os.path.exists(base_dir):
    print(base_dir)
else:
    print("path not found", base_dir)
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

# Initialize Flask app with both folders
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)


symbols_df = pd.read_csv("D:/Arkalogi/Project/Data/nifty50_symbols.csv")
symbols = symbols_df['tradingsymbol'].to_list()
download_day_data()
download_minute_data()

class company_validation(BaseModel):
    num : int
    symbol : str
    date_str : date

    @field_validator('symbol')
    def validate_symbol(cls, value):
        if value not in symbols:
            raise ValueError("This symbol is not in nifty50 symbols. Please try another symbol.")
        return value
    
class market_validation(BaseModel):
    num : int
    date_str : date

def get_close_price(base_dir, input_date, symbol):
    try:
        year, month, day = input_date.split("-")
        month_name = datetime.strptime(month, "%m").strftime("%b")

        file_path = os.path.join(base_dir,year, month_name, day, f"{symbol}.csv")

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return 0.0

        df = pd.read_csv(file_path)
        df.columns = [col.split('.')[-1] for col in df.columns] 

        result = df[df['Date'] == input_date]

        if not result.empty:
            return float(result.iloc[0]['Close'])
        else:
            print("Date not found in the file.")
            return 0.0

    except Exception as e:
        print("Error:", e)
        return 0.0

@app.route('/')
def home():
    markets = [{"name":"NIFTY 50","symbol":"^NSEI", "logo":"50"}, {"name":"NIFTY BANK","symbol":"^NSEBANK", "logo":"NB"}, {"name":"S&P BSE SENSEX ","symbol":"^BSESN", "logo":"30"}]
    tickers = []
    
    for item in markets:
        symbol = item["symbol"]
        download_ticker_day_data(symbol)
        download_minute_data_if_missing(symbol)

        data = pd.read_csv(f"D:/Arkalogi/Project/Data/Ticker_data/{symbol}.csv")
        value = round(data['Close'].iloc[-1],2)
        original_value = round(data['Close'].iloc[-2],2)
        change = round(((value - original_value) / original_value) * 100, 2)

        tickers.append({
            "name": item["name"],
            "symbol" : item["symbol"],
            "logo" : item["logo"],
            "value" : value,
            "change" : change,
        })

    return render_template('Home.html', tickers = tickers)

@app.route('/get_data')
def get_data():
    symbol = request.args.get('symbol')

    data = pd.read_csv(f"D:/Arkalogi/Project/Data/Ticker_data/{symbol}.csv")
    value = round(data['Close'].iloc[-1],2)
    original_value = round(data['Close'].iloc[-2],2)
    change_value = value - original_value
    change = round(( change_value / original_value) * 100, 2)
    sign = '+' if change_value > 0 else '-'

    return jsonify({
        'dates' : data['Date'].iloc[-250:].tolist(),
        'close': data['Close'].iloc[-250:].round(2).tolist(),
        'high' : data['High'].iloc[-250:].round(2).tolist(),
        'low' : data['Low'].iloc[-250:].round(2).tolist(),
        'change' : change,
        'sign': sign
    })

def get_intraday_data(symbol):
    date = datetime.now().date()
    date_str = date.strftime("%Y-%m-%d")
    year, month, day = date_str.split("-")
    month_name = datetime.strptime(month, "%m").strftime("%b")

    file_path = os.path.join("D:/Arkalogi/Project/Data/Ticker_Minute_data", year, month_name,day, f"{symbol}.csv")
    data = pd.read_csv(file_path)

    data['Time'] = pd.to_datetime(data['Time'])

    return data

def get_last_n_days_data(symbol, days):

    file_path = f"D:/Arkalogi/Project/Data/Ticker_data/{symbol}.csv"
    data = pd.read_csv(file_path)

    return data.iloc[-days:]

def get_default_data(symbol):
    file_path = f"D:/Arkalogi/Project/Data/Ticker_data/{symbol}.csv"
    data = pd.read_csv(file_path)

    return data

@app.route('/graph_page')
def graph_page():
    symbol = request.args.get('symbol')
    range = request.args.get('range', '1y')

    if symbol == '^NSEI':
        name = 'NIFTY 50'
    elif symbol == '^NSEBANK':
        name = 'NIFTY BANK'
    elif symbol == '^BSESN':
        name = 'S&P BSE SENSEX'
    else:
        name = ''

    if range == '1d':
        data = get_intraday_data(symbol)
        highest_value = data['High'].max()
        lowest_value = data['Low'].min()
        change = ((highest_value - lowest_value) / highest_value) * 100
        
        return jsonify({
            'name' : name,
            'labels': data['Time'].dt.strftime('%Y-%m-%dT%H:%M:%S').tolist(),
            'high': data['High'].round(2).tolist(),
            'low': data['Low'].round(2).tolist(),
            'change': change
        })
        
    elif range == '1w':
        data = get_last_n_days_data(symbol, 7)
    elif range == '1m':
        data = get_last_n_days_data(symbol, 30)
    elif range == '6m':
        data = get_last_n_days_data(symbol, 180)
    elif range == '1y':
        data = get_last_n_days_data(symbol, 365)
    else:
        data = get_default_data(symbol)

    highest_value = data['High'].max()
    lowest_value = data['Low'].min()
    change = ((highest_value - lowest_value) / highest_value) * 100
    data['Date'] = pd.to_datetime(data['Date'])  

    
    return jsonify({
        'name': name,
        'labels': data['Date'].dt.strftime('%Y-%m-%d').tolist(),
        'high': data['High'].round(2).tolist(),
        'low': data['Low'].round(2).tolist(),
        'change': change
    })

@app.route("/get_all_changes")
def get_all_changes():
    symbol = request.args.get("symbol", "^NSEI")
    ranges = ["1d", "1w", "1m", "6m", "1y"]
    result = {}

    for r in ranges:
        # Your logic here — this is dummy data
        if r == '1d':
            data = get_intraday_data(symbol)
            highest_value = data['High'].max()
            lowest_value = data['Low'].min()
            change = ((highest_value - lowest_value) / highest_value) * 100
        elif r == '1w':
            data = get_last_n_days_data(symbol, 7)
        elif r == '1m':
            data = get_last_n_days_data(symbol, 30)
        elif r == '6m':
            data = get_last_n_days_data(symbol, 180)
        elif r == '1y':
            data = get_last_n_days_data(symbol, 365)
        else:
            data = get_default_data(symbol)

        highest_value = data['High'].max()
        lowest_value = data['Low'].min()
        change = ((highest_value - lowest_value) / highest_value) * 100
        sign = "+" if change >= 0 else "-"
        result[r] = {"change": abs(change), "sign": sign}

    return jsonify(result)



@app.route('/market_form')
def market_form():
    return render_template('market.html', result = {}, Date = "")

@app.route('/company_form')
def company_form():
    return render_template('company.html', result = {})

@app.route('/pnl_form')
def pnl_form():
    return redirect(url_for('show_pnl_form'))

@app.route('/indicator_form')
def indicator_form():
    return redirect(url_for('show_indicator_form'))

@app.route('/company_insight', methods = ['POST', 'GET'])
def company_insight():
    if request.method == 'POST':
        num = int(request.form['num'])
        symbol = request.form['symbol']
        date_str = request.form['date']

        user_input = {
            "num" : num,
            "symbol": symbol,
            "date_str": date_str
        }

        try:
            company_validation(**user_input)
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            formated_date = date_obj.strftime("%d-%m-%Y")
            date = datetime.strptime(formated_date, "%d-%m-%Y").date()
            today = datetime.now().date()

            current_time = datetime.now().time()
            closing_time_str = "15:30:00"
            closing_time = datetime.strptime(closing_time_str, "%H:%M:%S").time()

            if date == today:
                current_date = today if current_time > closing_time else date - timedelta(days = 1)
            else:
                current_date = date

            current_date = current_date.strftime("%Y-%m-%d")
            ans = sma_calculation(symbol, current_date, num)
            sma = ans['SMA']
            close_price = round(get_close_price("D:/Arkalogi/Project/Data/Day_data", current_date, symbol), 2)

            if sma > close_price:
                recommendation = "BUY"
            elif sma < close_price:
                recommendation = "SELL"
            else:
                recommendation = "HOLD"

            result={
                "Date" : current_date,
                "Company" : symbol,
                "Close price" : close_price,
                "SMA" : sma,
                "Recommendation": recommendation,
            }

            return render_template('company.html', result = result)
        except ValueError as e:
            if "This symbol is not in nifty50 symbols. Please try another symbol." in str(e):
                popup_msg = "This symbol is not in nifty50 symbols. Please try another symbol."
            return render_template('company.html', popup = popup_msg, values= user_input)


@app.route('/market_insight', methods = ['POST', 'GET'])
def market_insight():
    if request.method == 'POST':
        result = []

        date_str = request.form['date']
        num = int(request.form['num'])

        user_input2 = {
            "date_str" : date_str,
            "num" : num
        }
        try:
            market_validation(**user_input2)

            for i in range(len(symbols_df)):
                symbol = symbols_df.loc[i, 'tradingsymbol']

                ans = sma_calculation(symbol, date_str, num)
                sma = ans['SMA']
                close_price = round(get_close_price("D:/Arkalogi/Project/Data/Day_data", date_str, symbol), 2)

                if sma > close_price:
                    recommendation = "BUY"
                elif sma < close_price:
                    recommendation = "SELL"
                else:
                    recommendation = "HOLD"

                result.append({
                    "Company" : symbol,
                    "ClosePrice" : close_price,
                    "SMA" : sma,
                    "Recommendation": recommendation,
                })

            return render_template('market.html', result = result, Date = date_str)
        except ValueError as e:
            popup_msg = str(e)
            return render_template('market.html', popup= popup_msg, values = user_input2)
        
class PnL(BaseModel):
    entry_date : date
    exit_date : date
    entry_time_str : str
    exit_time_str : str
    position : str
    symbol : str

    @field_validator('symbol')
    def validate_symbol(cls, value):
        if value not in symbols:
            raise ValueError(f"{value} is not in nifty50 symbols, Please try another symbol.")
        return value
    
    @model_validator(mode= 'after')
    def validate_times(self) -> 'PnL':
        
        parsed_entry_time = datetime.strptime(self.entry_time_str, '%H:%M').time()
        parsed_exit_time = datetime.strptime(self.exit_time_str, '%H:%M').time()

        if parsed_entry_time >= parsed_exit_time:
            raise ValueError("Entry time must be before Exit time")
        
        if not(time(9,15) <= parsed_entry_time <= time(15, 29)):
            raise ValueError("Entry time must be between 9:15 to 15:29")
        
        if not(time(9,15) <= parsed_exit_time <= time(15, 29)):
            raise ValueError("Exit time must be between 9:15 to 15:29")
        
        return self
        

@app.route('/form')
def show_pnl_form():
    return render_template('pnlOutput.html', result = {}, symbol="", popup = "")

@app.route('/pnlCalculation', methods=['POST'])
def pnlCalculation():
    if request.method == 'POST':
        entry_date = pd.to_datetime(request.form['entry_date'])
        exit_date = pd.to_datetime(request.form['exit_date'])
        entry_time_str = request.form['entry_time']
        exit_time_str = request.form['exit_time']
        position = request.form['position_type']
        symbol = request.form['symbol']

        user_input = {
            "entry_date" : entry_date,
            "exit_date" : exit_date,
            "entry_time_str" : entry_time_str,
            "exit_time_str" : exit_time_str,
            "position" : position,
            "symbol" : symbol
        }

        try: 
            PnL(**user_input)
            
            result = []
            current_date = entry_date
            while current_date < exit_date:
                current_date_str = current_date.strftime("%Y-%m-%d")
                year, month, day = current_date_str.split("-")
                month_name = datetime.strptime(month, '%m').strftime("%b")

                #base_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Data/Minute_data'))
                file_path = os.path.join("D:/Arkalogi/Project/Data/Minute_data", year, month_name, day, f"{symbol}.csv")


                try:
                    data = pd.read_csv(file_path)
                except FileNotFoundError:
                    print(f"{symbol}.csv file not found")
                    current_date += timedelta(days=1)
                    continue

                entry_close_price = None
                exit_close_price = None

                for i in range(len(data)):
                    current_time = pd.to_datetime(data.loc[i, 'Time'], format='%H:%M:%S').strftime('%H:%M')
                    if current_time == entry_time_str:
                        entry_close_price = data.loc[i, 'Close']
                    elif current_time == exit_time_str:
                        exit_close_price = data.loc[i, 'Close']
                    else:
                        continue

                if entry_close_price is None or exit_close_price is None:
                    print("entry or exit close price is none")
                    current_date += timedelta(days=1)
                    continue

                if position == 'short':
                    pnl = entry_close_price - exit_close_price
                elif position == 'long':
                    pnl = exit_close_price - entry_close_price

                result.append({

                    "Date" : current_date.strftime("%Y-%m-%d"),
                    "Entry_close_price" : round(entry_close_price, 2),
                    "Exit_close_price" : round(exit_close_price, 2),
                    "pnl" : round(pnl, 2)
                })

                current_date += timedelta(days=1)
        

            return render_template("pnlOutput.html", result = result, symbol=symbol, popup = "pnl Calculation successful")

        except ValueError as e:
             
            if "Entry time must be before Exit time" in str(e):
                popup_msg = "Entry time must be before Exit time"
            elif "Entry time must be between 9:15 to 15:29" in str(e):
                popup_msg = "Entry time must be between 9:15 to 15:29"
            elif "Exit time must be between 9:15 to 15:29" in str(e):
                popup_msg = "Exit time must be between 9:15 to 15:29"
            elif "This symbol is not in nifty50, try another symbol." in str(e):
                popup_msg = "This symbol is not in nifty50, try another symbol." 
            else:
                popup_msg = "An unknown error occurred."
                
            return render_template('pnlOutput.html',result = [], symbol= symbol, popup = popup_msg , values= user_input)

def get_rsi_signal(rsi):
    if rsi >= 60:
        return "Sell"
    elif rsi >= 40:
        return "Neutral"
    else:
        return "Buy"

def get_stochrsi_signal(val):
    if val >= 0.6:
        return "Sell"
    elif val >= 0.4:
        return "Neutral"
    else:
        return "Buy"

def get_moving_avg_signal(diff):
    if diff > 2:
        return "Sell"
    elif abs(diff) <= 2:
        return "Neutral"
    else:
        return "Buy"


@app.route('/indicator')
def show_indicator_form():
    return render_template('indicator.html')

@app.route('/indicators', methods=['POST'])
def indicators():
    if request.method == 'POST':
        symbol = request.form['symbol']
        date_str = request.form['date']
        
        selected_indicators = request.form.getlist('indicator')
        data={}

        for indicator in selected_indicators:
            w_key = f"{indicator}_window" 
            w_size = request.form.get(w_key)
            data[indicator] = w_size    

        result = []

        for indicator, w_size in data.items():
            if not w_size:
                continue  # Skip if window size not provided

            w_size = int(w_size)

            try:
                if indicator == 'SMA':
                    calculated_values = sma_calculation(symbol, date_str, w_size)
                    close_price = calculated_values['Close']
                    value = calculated_values['SMA']
                elif indicator == 'EMA':
                    calculated_values = EMA(symbol, date_str, w_size)
                    close_price = calculated_values['Close']
                    value = calculated_values['EMA']
                elif indicator == 'RSI':
                    calculated_values = RSI(symbol, date_str, w_size)
                    close_price = float(calculated_values['Close'].iloc[-1])
                    value = float(calculated_values['RSI'].iloc[-1])

                elif indicator == 'StochRSI':
                    calculated_values = StochRSI(symbol, date_str, w_size)
                    close_price = calculated_values['Close']
                    value = calculated_values['StochRSI']
                else:
                    continue  # Skip unknown indicators

                result.append({
                    "Date": date_str,
                    "Symbol": symbol,
                    "indicator": indicator,
                    "w_size": w_size,
                    "close": close_price,
                    "values": value
                })
            except Exception as e:
                import traceback
                print("[ERROR] Exception in indicator processing:", indicator)
                traceback.print_exc()
                result.append({
                    "indicator": indicator,
                    "error": str(e)
                })

        return jsonify(result)

@app.route('/widgets_form')
def widget_form():
    return render_template('widget.html', signals={}, final_result = {})


@app.route('/widgets', methods=['GET', 'POST'])
def widget_route():
    symbol = request.form.get("symbol")
    w_size = int(request.form.get("w_size"))

    data = widget(symbol, w_size)
    signals = []


    for item in data:
        if isinstance(item, dict):
            close_price = float(item.get('Close',0))
            if 'SMA' in item:
                sma = float(item['SMA'])
                diff = close_price - sma
                signal = get_moving_avg_signal(diff)
                signals.append(f"SMA: {signal}")
            elif 'EMA' in item:
                ema = float(item['EMA'])
                diff = close_price - ema
                signal = get_moving_avg_signal(diff)
                signals.append(f"EMA: {signal}")
            elif 'StochRSI' in item:
                stochRsi = float(item['StochRSI'])
                signal = get_stochrsi_signal(stochRsi)
                signals.append(f"StochRSI: {signal}")
        elif isinstance(item, pd.Series):
            rsi = float(item.get('RSI',0))
            signal = get_rsi_signal(rsi)
            signals.append(f"RSI: {signal}")

    buy = sum("Buy" in s for s in signals)
    sell = sum("Sell" in s for s in signals)

    if(buy > sell):
        final_result = "Buy"
    elif (sell > buy):
        final_result="Sell"
    else:
        final_result= "Neutral"

    print({"final_signal": final_result, "singals": signals})

    return render_template('widget.html', final_result= final_result, signals = signals, symbol = symbol, w_size = w_size)


if __name__ == '__main__':
    app.run(debug = True)
