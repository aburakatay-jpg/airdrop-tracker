import requests

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID
)


def send_message(text):
    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):
        print(
            "Telegram ayarları eksik; "
            "bildirim atlanıyor."
        )
        return False

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/"
        f"sendMessage"
    )

    # Telegram mesaj limiti nedeniyle
    # uzun mesajları parçalara böl.
    chunks = [
        text[i:i + 3900]
        for i in range(
            0,
            len(text),
            3900
        )
    ]

    all_ok = True

    for chunk in chunks:
        try:
            response = requests.post(
                url,
                json={
                    "chat_id": (
                        TELEGRAM_CHAT_ID
                    ),
                    "text": chunk,
                    "disable_web_page_preview": True
                },
                timeout=15
            )

            if not response.ok:
                print(
                    "Telegram API hatası: "
                    f"{response.status_code} "
                    f"- {response.text}"
                )

                all_ok = False

        except Exception as e:
            print(
                "Telegram bağlantı hatası: "
                f"{e}"
            )

            all_ok = False

    return all_ok


def format_airdrop_message(
    item
):
    steps = (
        item.get(
            "action_plan_steps"
        )
        or []
    )

    risks = (
        item.get(
            "risks"
        )
        or []
    )

    checklist = (
        item.get(
            "verification_checklist"
        )
        or []
    )

    step_text = "\n".join(
        str(step)
        for step in steps[:10]
    )

    if not step_text:
        step_text = (
            "Adım üretilemedi."
        )

    risk_text = "\n".join(
        f"- {risk}"
        for risk in risks[:6]
    )

    if not risk_text:
        risk_text = (
            "- Belirgin risk kaydı yok."
        )

    checklist_text = "\n".join(
        f"- {check}"
        for check in checklist[:6]
    )

    if not checklist_text:
        checklist_text = (
            "- Kontrol listesi üretilemedi."
        )

    estimated_cost = (
        item.get(
            "estimated_cost_usd"
        )
    )

    if estimated_cost is None:
        cost_text = (
            "Bilinmiyor"
        )
    else:
        cost_text = (
            f"${estimated_cost}"
        )

    official_url = (
        item.get(
            "official_url"
        )
        or "Doğrulanamadı"
    )

    message = (
        f"🚀 "
        f"{item.get('project_name', 'Bilinmeyen Proje')}"
        f"\n\n"

        f"Durum: "
        f"{item.get('status', 'WATCH')}"
        f"\n"

        f"Airdrop Skoru: "
        f"{item.get('airdrop_score', 0)}/100"
        f"\n"

        f"Ücretsiz Katılım Skoru: "
        f"{item.get('free_score', 0)}/100"
        f"\n"

        f"Güven Skoru: "
        f"{item.get('confidence_score', 0)}/100"
        f"\n"

        f"Tahmini Maliyet: "
        f"{cost_text}"
        f"\n"

        f"Token Durumu: "
        f"{item.get('token_status', 'unknown')}"
        f"\n"

        f"Risk Seviyesi: "
        f"{item.get('risk_level', 'MEDIUM')}"
        f"\n\n"

        f"💡 Neden?\n"
        f"{item.get('reasoning', '')}"
        f"\n\n"

        f"⏱ Neden şimdi?\n"
        f"{item.get('why_now', '')}"
        f"\n\n"

        f"🧭 Nasıl katılırım?\n"
        f"{step_text}"
        f"\n\n"

        f"⚠️ Riskler\n"
        f"{risk_text}"
        f"\n\n"

        f"🛡️ Kontrol Listesi\n"
        f"{checklist_text}"
        f"\n\n"

        f"🔗 Resmi / Önerilen URL:\n"
        f"{official_url}"
    )

    return message
