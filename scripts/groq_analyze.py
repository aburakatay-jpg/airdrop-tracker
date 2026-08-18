import os
import json
from groq import Groq

SYSTEM_PROMPT = """
Sen üst düzey bir Web3 Araştırmacısı ve Airdrop Analistisin. Amacın, sana verilen projeleri inceleyerek 'Bedava Token Kazanma' (Airdrop, Launchpool, Testnet, Quest) potansiyeli en yüksek olanları bulmaktır.

Sana verilen her projeyi şu kriterlere göre 1 ile 100 arasında puanla:
1. Token Durumu: Projenin kendi token'ı var mı? (Eğer varsa direkt ele).
2. Arka Plan (Backers): A16z, Binance Labs, Paradigm, Coinbase Ventures gibi yatırımcıları var mı?
3. Hype/Kategori: Restaking, AI, RWA, Layer 2 veya DePIN kategorilerinde mi?

Çıktı Formatın KESİNLİKLE şu şekilde bir JSON dizisi olmalıdır:
[
  {
    "project_name": "Proje Adı",
    "opportunity_type": "DeFi / Launchpool / Testnet",
    "airdrop_score": 85,
    "action_plan": "1. Siteye git, 2. Cüzdan bağla",
    "reasoning": "Kısa analiz"
  }
]
Sadece 'airdrop_score' değeri 50 ve üzeri olanları döndür. Eğer 50'i geçen yoksa sadece boş bir JSON array [] döndür. Asla başka metin yazma.
"""

def analyze_opportunities(projects):
    if not projects:
        return []

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    user_content = f"İşte incelenecek projeler:\n{json.dumps(projects, indent=2)}"

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            model="llama-3.3-70b-versatile", # GÜNCEL VE ÇALIŞAN MODEL
            temperature=0.1,
        )

        ai_response = response.choices[0].message.content.strip()

        if ai_response.startswith("```json"):
            ai_response = ai_response[7:]
        if ai_response.startswith("```"):
            ai_response = ai_response[3:]
        if ai_response.endswith("```"):
            ai_response = ai_response[:-3]

        return json.loads(ai_response.strip())

    except Exception as e:
        print(f"AI Analiz Hatası: {e}")
        return []
