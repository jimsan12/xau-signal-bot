import time
import requests
import telebot
from datetime import datetime

# --- Telegram Setup ---
BOT_TOKEN = "7728743162:AAGYJxW59keeshlgdrM0bBz8pCa0kEuJPbc"
CHAT_ID = "8127758686"
bot = telebot.TeleBot(BOT_TOKEN)

# --- Financial Modeling Prep API ---
API_KEY = "nsfStQOyx0wc8YAbUdsELJ0u2o7wBabE"

# --- Fetch XAU/USD data for a given timeframe ---
def fetch_data(interval):
    url = f"https://financialmodelingprep.com/api/v3/technical_indicator/1min/XAUUSD?period=14&type=rsi&apikey={API_KEY}"
    try:
        rsi_data = requests.get(url).json()
        if not rsi_data:
            return None
        return rsi_data[0]["rsi"]
    except:
        return None

# --- Main Signal Checker ---
def check_signals():
    rsi_15m = fetch_data("15min")
    rsi_1h = fetch_data("1hour")

    if rsi_15m is None or rsi_1h is None:
        return None

    # --- Example logic ---
    if rsi_15m < 30 and rsi_1h < 30:
        # Strong Buy setup
        entry = 2450.00
        tp = entry + 3.50
        sl = entry - 2.00
        return f"📈 STRONG BUY XAU/USD\nTP: {tp}\nSL: {sl}\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    elif rsi_15m > 70 and rsi_1h > 70:
        # Strong Sell setup
        entry = 2450.00
        tp = entry - 3.50
        sl = entry + 2.00
        return f"📉 STRONG SELL XAU/USD\nTP: {tp}\nSL: {sl}\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    else:
        return None

# --- Notify startup ---
bot.send_message(CHAT_ID, "🤖 Gold Signal Bot Connected ✅\n🔍 Scanning XAU/USD every 5 minutes...")

last_no_signal = 0

while True:
    try:
        signal = check_signals()
        now = time.time()

        if signal:
            bot.send_message(CHAT_ID, signal)
        elif now - last_no_signal >= 3600:
            bot.send_message(CHAT_ID, "🔸 No strong signal found in the last hour.")
            last_no_signal = now

    except Exception as e:
        bot.send_message(CHAT_ID, f"⚠️ Bot Error: {e}")

    time.sleep(300)  # Wait 5 minutes
