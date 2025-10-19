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

# --- File to save crash logs ---
LOG_FILE = "bot_error_log.txt"

# --- Helper: log errors to file ---
def log_error(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} - {message}\n")

# --- Function to fetch and analyze XAU/USD data ---
def check_market_for_signals():
    try:
        response = requests.get(API_URL)
        data = response.json()

        # Find XAU/USD pair
        gold_data = next((item for item in data if item["symbol"] == "XAU/USD"), None)
        if not gold_data:
            bot.send_message(CHAT_ID, "⚠️ XAU/USD data not found.")
            return

        price = gold_data["price"]
        change = gold_data.get("changesPercentage", 0)

        # --- Example logic for strong signal ---
        if change > 0.35:
            # Strong upward momentum
            entry = round(price, 2)
            tp = round(entry + 3.00, 2)
            sl = round(entry - 2.00, 2)
            bot.send_message(CHAT_ID, f"📈 STRONG BUY XAU/USD\nEntry: {entry}\nTP: {tp}\nSL: {sl}\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        elif change < -0.35:
            # Strong downward momentum
            entry = round(price, 2)
            tp = round(entry - 3.00, 2)
            sl = round(entry + 2.00, 2)
            bot.send_message(CHAT_ID, f"📉 STRONG SELL XAU/USD\nEntry: {entry}\nTP: {tp}\nSL: {sl}\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("No strong signal found at this time.")

    except Exception as e:
        log_error(f"Signal check failed: {e}")
        bot.send_message(CHAT_ID, f"⚠️ Error while checking market: {e}")

# --- On startup ---
bot.send_message(CHAT_ID, "✅ Bot deployed successfully and is now active. Scanning XAU/USD market...")

# --- Main loop ---
while True:
    try:
        # Notify active status
        bot.send_message(CHAT_ID, "🟢 Bot Active — scanning XAU/USD market for strong signals...")

        # Perform analysis
        check_market_for_signals()

    except Exception as e:
        error_message = f"⚠️ Bot Error Detected: {e}"
        log_error(error_message)
        bot.send_message(CHAT_ID, f"{error_message}\nAttempting auto-restart...")
        time.sleep(10)
        continue  # auto-restart

    # Wait 5 minutes before next scan
    time.sleep(300)
