import requests
import os

TELEGRAM_BOT_TOKEN = os.environ.get("8922380269:AAHwnnGldeomfJV4PoRPmbv2RuycKQiFhmU")
TELEGRAM_CHAT_ID = os.environ.get("8922380269")

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Yanit: {response.text}")
    return response.ok

send_message("Test mesaji")
