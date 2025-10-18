
import requests

# 1️⃣ Put your bot token and chat ID here
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

# 2️⃣ Write the test signal message
message = "✅ Test Signal: XAU/USD\nTP: 1950\nSL: 1930"

# 3️⃣ Send the message to Telegram
requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={"chat_id": CHAT_ID, "text": message}
)
