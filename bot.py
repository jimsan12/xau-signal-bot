import requests
import datetime
import pytz
import time
import telebot

# =======================
# 🔧 CONFIGURATION
# =======================
BOT_TOKEN = "7728743162:AAGYJxW59keeshlgdrM0bBz8pCa0kEuJPbc"
CHAT_ID = "8127758686"

PAIR = "XAUUSD=X"  # Gold/USD pair on Yahoo Finance
TIMEZONE = pytz.timezone("Africa/Lagos")

bot = telebot.TeleBot(BOT_TOKEN)

# =======================
# 📊 FETCH DATA FUNCTION
# =======================
def get_data(interval="15m"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{PAIR}?interval={interval}&range=1d"
    response = requests.get(url)
    data = response.json()

    try:
        timestamps = data["chart"]["result"][0]["timestamp"]
        close_prices = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        last_price = close_prices[-1]
        return last_price
    except Exception as e:
        print(f"⚠️ Error fetching {interval} data: {e}")
        return None


# =======================
# 📈 MARKET SCAN
# =======================
def scan_market():
    try:
        price_15m = get_data("15m")
        price_1h = get_data("1h")

        if price_15m is None or price_1h is None:
            bot.send_message(chat_id=CHAT_ID, text="⚠️ Error fetching data. Retrying...")
            return

        now = datetime.datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

        # Example confirmation check
        if price_15m > price_1h:
            bot.send_message(chat_id=CHAT_ID, text=f"🟢 BUY SIGNAL ({PAIR})\nPrice: {price_15m}\nTime: {now}")
        elif price_15m < price_1h:
            bot.send_message(chat_id=CHAT_ID, text=f"🔴 SELL SIGNAL ({PAIR})\nPrice: {price_15m}\nTime: {now}")
        else:
            print(f"{now} — No signal at the moment.")

    except Exception as e:
        print(f"⚠️ Error in debug scan: {e}")


# =======================
# 🕒 CHECK IF MARKET IS CLOSED
# =======================
def market_is_closed():
    now = datetime.datetime.now(TIMEZONE)
    # Market closed on Saturday (5) and Sunday (6)
    return now.weekday() in [5, 6]


# =======================
# 🚀 MAIN LOOP
# =======================
def main():
    bot.send_message(chat_id=CHAT_ID, text="🤖 Gold Signal Bot connected successfully ✅")
    print("Bot started successfully...")

    while True:
        try:
            if market_is_closed():
                now = datetime.datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
                print(f"{now} — Market closed, sleeping for 1 hour.")
                time.sleep(3600)
                continue

            scan_market()

            # Keep-alive print every 2 hours
            if datetime.datetime.now().minute == 0:
                print("⏱️ Keep-alive ping to Render")

            time.sleep(300)  # 5 minutes between scans

        except Exception as e:
            print(f"⚠️ Bot error: {e}")
            time.sleep(30)
            continue


if __name__ == "__main__":
    main()
