import requests
import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_message(text):
    url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload)
    return response.ok

def notify_new_candidates(candidates):
    if not candidates:
        print("Bildirim gönderilecek aday yok.")
        return

    send_message("🪂 Airdrop Radar — " + str(len(candidates)) + " Yeni Aday")

    for c in candidates:
        tvl_m = c["tvl"] / 1_000_000
        msg = (
            "📌 " + c["name"] + "\n"
            "💰 TVL: $" + str(round(tvl_m, 1)) + "M\n"
            "⛓️ Zincir: " + c["chain"] + "\n"
            "📂 Kategori: " + c["category"] + "\n"
            "🔗 " + (c.get("url") or "Link yok")
        )
        send_message(msg)
        print("Gönderildi: " + c["name"])

if __name__ == "__main__":
    notify_new_candidates([
        {
            "name": "Test Protokol",
            "tvl": 150_000_000,
            "chain": "Ethereum",
            "category": "Lending",
            "url": "https://example.com"
        }
    ])