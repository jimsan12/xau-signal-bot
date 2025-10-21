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
    return requests.get(url).json()["chart"]["result"][0]["indicators"]["quote"][0]["close"]

def calc_rsi(prices):
    deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
    gain = sum(x for x in deltas[-14:] if x > 0) / 14
    loss = -sum(x for x in deltas[-14:] if x < 0) / 14
    if loss == 0: return 100
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def check_signals():
    try:
        p5, p1 = get_prices("5m"), get_prices("1h")
        rsi5, rsi1 = calc_rsi(p5[-20:]), calc_rsi(p1[-20:])
        price = round(p5[-1], 2)

        if rsi5 < 30 and rsi1 < 30:
            bot.send_message(CHAT_ID, f"📈 BUY XAU/USD\nEntry: {price}\nTP: {price + 3:.2f}\nSL: {price - 2:.2f}\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        elif rsi5 > 70 and rsi1 > 70:
            bot.send_message(CHAT_ID, f"📉 SELL XAU/USD\nEntry: {price}\nTP: {price - 3:.2f}\nSL: {price + 2:.2f}\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        bot.send_message(CHAT_ID, f"⚠️ Error: {e}")

bot.send_message(CHAT_ID, "✅ Bot started successfully! Scanning every 5 minutes...")

while True:
    check_signals()
    time.sleep(300)
