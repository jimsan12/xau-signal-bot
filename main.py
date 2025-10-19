import random
import time
from datetime import datetime
import pytz
import requests

# === CONFIGURATION ===
BOT_NAME = "XAU/USD SIGNAL BOT"
PAIR = "XAU/USD"

# === TELEGRAM CONFIG ===
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID_HERE"

# === SIGNAL GENERATOR FUNCTION ===
def generate_signal():
    price = round(random.uniform(2400, 2450), 2)
    tp = round(price + random.uniform(3, 6), 2)
    sl = round(price - random.uniform(2, 4), 2)
    return {
        "pair": PAIR,
        "price": price,
        "tp": tp,
        "sl": sl,
        "timestamp": datetime.now(pytz.timezone("Africa/Lagos")).strftime("%Y-%m-%d %H:%M:%S")
    }

# === TELEGRAM SEND FUNCTION ===
def send_to_telegram(signal):
    message = f"""
📊 *{BOT_NAME}*

PAIR: {signal['pair']}
ENTRY: {signal['price']}
🎯 TP: {signal['tp']}
🛑 SL: {signal['sl']}

🕒 {signal['timestamp']} (Lagos)
"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=data)

# === MAIN LOOP ===
print("Bot started successfully...")

while True:
    signal = generate_signal()
    send_to_telegram(signal)
    print(f"Signal sent: {signal}")
    time.sleep(3600)  # sends every 1 hour
