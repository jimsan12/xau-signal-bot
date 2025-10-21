import time
import requests
import telebot
from datetime import datetime

BOT_TOKEN = "7728743162:AAGYJxW59keeshlgdrM0bBz8pCa0kEuJPbc"
CHAT_ID = "8127758686"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "🤖 Gold Signal Bot is active ✅")

def get_prices(interval):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/XAUUSD=X?interval={interval}&range=1d"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print(f"Yahoo API error ({r.status_code})")
            return None
        data = r.json()
        return data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    except Exception as e:
        print(f"Price fetch failed: {e}")
        return None

def calc_rsi(prices):
    if not prices or len(prices) < 15:
        return 50
    deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
    gain = sum(x for x in deltas[-14:] if x > 0) / 14
    loss = -sum(x for x in deltas[-14:] if x < 0) / 14
    if loss == 0: return 100
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def check_signals():
    try:
        p5 = get_prices("5m")
        p1 = get_prices("1h")
        if not p5 or not p1:
            bot.send_message(CHAT_ID, "⚠️ Data unavailable (Yahoo delay). Retrying in 5 mins...")
            return

        rsi5, rsi1 = calc_rsi(p5[-20:]), calc_rsi(p1[-20:])
        price = round(p5[-1], 2)

        if rsi5 < 30 and rsi1 < 30:
            bot.send_message(CHAT_ID, f"📈 BUY XAU/USD\nEntry: {price}\nTP: {price + 3:.2f}\nSL: {price - 2:.2f}\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        elif rsi5 > 70 and rsi1 > 70:
            bot.send_message(CHAT_ID, f"📉 SELL XAU/USD\nEntry: {price}\nTP: {price - 3:.2f}\nSL: {price + 2:.2f}\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        bot.send_message(CHAT_ID, f"⚠️ Error checking market: {e}")

bot.send_message(CHAT_ID, "✅ Bot started successfully! Scanning every 5 minutes...\n⏰ Sending active updates every 30 minutes...")

last_update = time.time()

while True:
    check_signals()

    # Every 30 minutes → confirmation message
    if time.time() - last_update >= 1800:
        bot.send_message(CHAT_ID, f"✅ Bot still active — {datetime.now().strftime('%H:%M:%S')}")
        last_update = time.time()

    time.sleep(300)
