import time
import requests
import telebot
from datetime import datetime

# --- Telegram setup ---
BOT_TOKEN = "7728743162:AAGYJxW59keeshlgdrM0bBz8pCa0kEuJPbc"
CHAT_ID = "8127758686"
bot = telebot.TeleBot(BOT_TOKEN)

# --- FinancialModelingPrep setup ---
API_KEY = "nsfStQOyx0wc8YAbUdsELJ0u2o7wBabE"

# --- Helper: Get current price ---
def get_price(symbol="XAU/USD"):
    try:
        url = f"https://financialmodelingprep.com/api/v3/quotes/forex?apikey={API_KEY}"
        data = requests.get(url, timeout=10).json()
        gold = next((item for item in data if item["symbol"] == symbol), None)
        return gold["price"] if gold else None
    except:
        return None

# --- Get RSI and EMA Data ---
def get_signal():
    try:
        rsi_5 = requests.get(f"https://financialmodelingprep.com/api/v3/technical_indicator/5min/XAUUSD?period=14&type=rsi&apikey={API_KEY}", timeout=10).json()
        rsi_15 = requests.get(f"https://financialmodelingprep.com/api/v3/technical_indicator/15min/XAUUSD?period=14&type=rsi&apikey={API_KEY}", timeout=10).json()
        ema_5 = requests.get(f"https://financialmodelingprep.com/api/v3/technical_indicator/5min/XAUUSD?period=20&type=ema&apikey={API_KEY}", timeout=10).json()

        if not rsi_5 or not rsi_15 or not ema_5:
            return None

        rsi5 = float(rsi_5[-1]["rsi"])
        rsi15 = float(rsi_15[-1]["rsi"])
        ema20 = float(ema_5[-1]["ema"])
        price = get_price()

        if not price:
            return None

        # --- STRONG BUY ---
        if rsi5 < 30 and rsi15 < 30 and price > ema20:
            tp = round(price + 3, 2)
            sl = round(price - 2, 2)
            return f"📈 STRONG BUY XAU/USD\nTP: {tp}\nSL: {sl}\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        # --- STRONG SELL ---
        elif rsi5 > 70 and rsi15 > 70 and price < ema20:
            tp = round(price - 3, 2)
            sl = round(price + 2, 2)
            return f"📉 STRONG SELL XAU/USD\nTP: {tp}\nSL: {sl}\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return None
    except:
        return None

# --- Check if market is open (Mon–Fri) ---
def market_open():
    weekday = datetime.utcnow().weekday()  # Monday = 0, Sunday = 6
    return weekday < 5

# --- Send startup message ---
bot.send_message(CHAT_ID, "🤖 Bot connected successfully ✅")
bot.send_message(CHAT_ID, "🔍 Scanning XAU/USD every 5 minutes (Mon–Fri only)...")

# --- Continuous scanning loop ---
counter = 0
market_closed = False  # Track market close status

while True:
    try:
        if not market_open():
            if not market_closed:
                bot.send_message(CHAT_ID, f"⏸ Market closed — Bot sleeping until Monday. ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
                market_closed = True
            time.sleep(3600)  # Check every hour during weekends
            continue
        else:
            if market_closed:
                bot.send_message(CHAT_ID, f"✅ Market reopened — Bot resumed scanning. ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
                market_closed = False

        signal = get_signal()
        if signal:
            bot.send_message(CHAT_ID, signal)
            counter = 0
        else:
            counter += 1
            if counter >= 6:
                bot.send_message(CHAT_ID, f"ℹ️ No strong signal yet. Bot still active — {datetime.now().strftime('%H:%M:%S')}")
                counter = 0

        time.sleep(300)  # Wait 5 minutes
    except Exception as e:
        bot.send_message(CHAT_ID, f"⚠️ Bot error: {e}\nAuto-restarting...")
        time.sleep(10)
        continue
