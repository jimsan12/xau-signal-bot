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
API_URL = f"https://financialmodelingprep.com/api/v3/quotes/forex?apikey={API_KEY}"

# --- Startup ---
bot.send_message(CHAT_ID, "🤖 Gold Signal Bot (Debug Mode) started successfully!\n🔍 Scanning XAU/USD every 5 minutes...")

def check_market_debug():
    try:
        response = requests.get(API_URL)
        data = response.json()

        gold_data = next((item for item in data if item["symbol"] == "XAU/USD"), None)
        if not gold_data:
            bot.send_message(CHAT_ID, "⚠️ XAU/USD data not found.")
            return

        price = gold_data["price"]
        change = gold_data.get("changesPercentage", 0)

        # Dummy RSI/EMA values for debugging (since FMP doesn’t give them directly)
        # We'll simulate values that change slightly each time
        rsi = 50 + (change * 10)
        ema20 = round(price - (change * 2), 2)

        # Send live data preview
        msg = (
            f"📊 *Live Market Check (Debug)*\n"
            f"Symbol: XAU/USD\n"
            f"Price: {price}\n"
            f"RSI: {rsi:.2f}\n"
            f"EMA20: {ema20}\n"
            f"Change%: {change:.3f}\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")

        # Quick signal example
        if change > 0.35:
            bot.send_message(CHAT_ID, f"📈 BUY detected — TP: {round(price + 3,2)} | SL: {round(price - 2,2)}")
        elif change < -0.35:
            bot.send_message(CHAT_ID, f"📉 SELL detected — TP: {round(price - 3,2)} | SL: {round(price + 2,2)}")

    except Exception as e:
        bot.send_message(CHAT_ID, f"⚠️ Error in debug scan: {e}")

# --- Main loop ---
while True:
    check_market_debug()
    time.sleep(300)  # wait 5 minutes
