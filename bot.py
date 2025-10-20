import requests
import time
import pytz
from datetime import datetime

# === CONFIG ===
API_KEY = "nsfStQOyx0wc8YAbUdsELJ0u2o7wBabE"  # FinancialModelingPrep key
BOT_TOKEN = "7728743162:AAGYJxW59keeshlgdrM0bBz8pCa0kEuJPbc"
CHAT_ID = "8127758686"

def send_telegram_message(message):
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": message})
    except Exception as e:
        print(f"⚠️ Telegram error: {e}")

def fetch_gold_data():
    """Fetch XAU/USD data safely"""
    url = f"https://financialmodelingprep.com/api/v3/quotes/forex?apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        # ✅ Fix for 'string indices' error
        gold_data = None
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("symbol") == "XAU/USD":
                    gold_data = item
                    break

        if not gold_data:
            raise ValueError("No XAU/USD data found")

        return gold_data

    except Exception as e:
        send_telegram_message(f"⚠️ Error fetching data: {e}")
        print(f"⚠️ Error fetching data: {e}")
        return None

def main():
    """Main loop"""
    print("🤖 Debug bot started...")
    send_telegram_message("✅ Debug bot started successfully!")

    while True:
        try:
            data = fetch_gold_data()
            if data:
                price = data.get("price")
                timestamp = datetime.now(pytz.timezone("Africa/Lagos")).strftime("%Y-%m-%d %H:%M:%S")
                message = f"💰 Gold Price: {price}\n🕒 Time: {timestamp}"
                send_telegram_message(message)
                print(message)
            else:
                print("⚠️ No valid data found this round.")

        except Exception as e:
            send_telegram_message(f"⚠️ Error in debug scan: {e}")
            print(f"⚠️ Error in debug scan: {e}")

        time.sleep(300)  # Run every 5 minutes

if __name__ == "__main__":
    main()
