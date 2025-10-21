import requests
import time
import datetime
import telebot

# ========================
# CONFIGURATION
# ========================
BOT_TOKEN = "7728743162:AAGYJxW59keeshlgdrM0bBz8pCa0kEuJPbc"
API_KEY = "29d871f9d28f4642b7a43496bf1393ee"
SYMBOL = "XAU/USD"
INTERVAL_1 = "15min"
INTERVAL_2 = "1h"

bot = telebot.TeleBot(BOT_TOKEN)

# ========================
# FUNCTIONS
# ========================

def get_price_data(symbol, interval):
    """Fetch latest candle data from Twelve Data"""
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&apikey={API_KEY}&outputsize=5"
    r = requests.get(url)
    data = r.json()
    if "values" not in data:
        raise ValueError(str(data))
    return data["values"]

def rsi_calc(data):
    """Simple RSI calculator"""
    closes = [float(x["close"]) for x in data[::-1]]
    gains = []
    losses = []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        if diff >= 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))
    avg_gain = sum(gains) / len(gains)
    avg_loss = sum(losses) / len(losses)
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def ema_calc(data, period=20):
    """EMA calculation"""
    closes = [float(x["close"]) for x in data[::-1]]
    k = 2 / (period + 1)
    ema = closes[0]
    for price in closes[1:]:
        ema = price * k + ema * (1 - k)
    return ema

def analyze():
    """Analyze dual timeframe and send signal"""
    data15 = get_price_data(SYMBOL, INTERVAL_1)
    data1h = get_price_data(SYMBOL, INTERVAL_2)

    rsi15 = rsi_calc(data15)
    rsi1h = rsi_calc(data1h)
    ema20 = ema_calc(data15)
    price = float(data15[0]["close"])

    signal = None
    if rsi15 < 30 and rsi1h < 30 and price > ema20:
        signal = f"🟢 BUY Signal for {SYMBOL}\n💰 Price: {price}\n🎯 TP: {price+2}\n⛔ SL: {price-1}\n⏰ {datetime.datetime.utcnow()} UTC"
    elif rsi15 > 70 and rsi1h > 70 and price < ema20:
        signal = f"🔴 SELL Signal for {SYMBOL}\n💰 Price: {price}\n🎯 TP: {price-2}\n⛔ SL: {price+1}\n⏰ {datetime.datetime.utcnow()} UTC"

    if signal:
        bot.send_message(chat_id="8127758686", text=signal)
    else:
        print("No signal this round")

# ========================
# MAIN LOOP
# ========================
bot.send_message(chat_id="8127758686", text="🤖 Gold Signal Bot started successfully ✅")
while True:
    try:
        analyze()
    except Exception as e:
        bot.send_message(chat_id="8127758686", text=f"⚠️ Error: {e}")
    time.sleep(300)  # 5 minutes
