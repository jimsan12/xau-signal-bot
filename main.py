import time
from datetime import datetime
import pytz
import requests
from flask import Flask
import threading
import pandas as pd

# === CONFIGURATION ===
PAIR = "XAU/USD"
API_KEY = "YOUR_API_KEY_HERE"  # from financialmodelingprep.com

# === TELEGRAM ===
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID_HERE"

# === FETCH PRICE DATA ===
def get_price_history(interval="5min"):
    try:
        url = f"https://financialmodelingprep.com/api/v3/historical-chart/{interval}/XAUUSD?apikey={API_KEY}"
        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data)
        df['close'] = df['close'].astype(float)
        df = df.head(100)[::-1]  # last 100 candles, latest last
        return df
    except Exception as e:
        print(f"⚠️ Error fetching {interval} data: {e}")
        return None

# === INDICATORS ===
def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_ema(df, period=20):
    return df['close'].ewm(span=period, adjust=False).mean().iloc[-1]

# === DUAL-TIMEFRAME STRONG SIGNAL LOGIC ===
def generate_signal():
    df_5 = get_price_history("5min")
    df_15 = get_price_history("15min")
    if df_5 is None or df_15 is None:
        return None

    price = df_5['close'].iloc[-1]

    ema20_5 = calculate_ema(df_5, 20)
    ema20_15 = calculate_ema(df_15, 20)

    rsi_5 = calculate_rsi(df_5)
    rsi_15 = calculate_rsi(df_15)

    signal = None

    # STRONG BUY: RSI < 30 on both timeframes and price > both EMAs
    if rsi_5 < 30 and rsi_15 < 30 and price > ema20_5 and price > ema20_15:
        tp = round(price + 5, 2)
        sl = round(price - 3, 2)
        signal = {"type": "BUY", "entry": round(price, 2), "tp": tp, "sl": sl}

    # STRONG SELL: RSI > 70 on both timeframes and price < both EMAs
    elif rsi_5 > 70 and rsi_15 > 70 and price < ema20_5 and price < ema20_15:
        tp = round(price - 5, 2)
        sl = round(price + 3, 2)
        signal = {"type": "SELL", "entry": round(price, 2), "tp": tp, "sl": sl}

    return signal

# === TELEGRAM MESSAGE ===
def send_to_telegram(signal):
    lagos_tz = pytz.timezone("Africa/Lagos")
    lagos_time = datetime.now(lagos_tz).strftime("%Y-%m-%d %H:%M:%S")

    message = f"""
{signal['type']} {PAIR}
💰 Entry: {signal['entry']}
🎯 TP: {signal['tp']}
🛑 SL: {signal['sl']}
⏰ Time: {lagos_time}
"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

# === FLASK SERVER (for Render) ===
app = Flask(__name__)

@app.route('/')
def home():
    return "XAU/USD Dual-Timeframe Strong Signal Bot running"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# === MAIN LOOP ===
def run_bot():
    print("🤖 Dual-Timeframe Bot started... scanning every 5 minutes for strong confirmations.")
    last_signal = None
    last_sent_hour = None

    while True:
        lagos_tz = pytz.timezone("Africa/Lagos")
        current_hour = datetime.now(lagos_tz).strftime("%Y-%m-%d %H")

        signal = generate_signal()
        if signal and signal != last_signal and current_hour != last_sent_hour:
            send_to_telegram(signal)
            print(f"✅ Sent STRONG DUAL signal: {signal}")
            last_signal = signal
            last_sent_hour = current_hour
        else:
            print("⏳ No strong dual-confirmation signal, rechecking in 5 minutes...")
        time.sleep(300)  # every 5 minutes

# === RUN BOTH THREADS ===
threading.Thread(target=run_flask).start()
threading.Thread(target=run_bot).start()
