import requests
import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("HATA: TELEGRAM_BOT_TOKEN veya TELEGRAM_CHAT_ID ortam değişkenlerinde bulunamadı!")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.ok:
            print("Telegram mesajı başarıyla gönderildi.")
            return True
        else:
            print(f"Telegram API Hatası: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Telegram bağlantı hatası: {e}")
        return False

if __name__ == "__main__":
    # Test etmek için:
    test_sonucu = send_message("<b>Airdrop Radar Test</b>\nBot başarıyla bağlandı!")
    print(f"Test sonucu: {test_sonucu}")
