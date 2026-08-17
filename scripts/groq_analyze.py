import os
import json
from groq import Groq

# Senin yazdığın o harika prompt
SYSTEM_PROMPT = """
Sen üst düzey bir Web3 Araştırmacısı ve Airdrop Analistisin. Amacın, sana verilen veri kaynaklarındaki (DeFi, Borsalar, Sosyal Medya) projeleri inceleyerek 'Bedava Token Kazanma' (Airdrop, Launchpool, Testnet, Quest) potansiyeli en yüksek olanları bulmaktır.

Sana verilen her projeyi şu kriterlere göre 1 ile 100 arasında puanla:
1. Token Durumu: Projenin kendi token'ı var mı? (Eğer varsa ve yeni bir kampanya değilse direkt ele).
2. Arka Plan (Backers): A16z, Binance Labs, Paradigm, Coinbase Ventures gibi Tier-1 yatırımcıları var mı? (Varsa +30 puan).
3. Hype/Kategori: Restaking, AI, RWA, Layer 2 veya DePIN kategorilerinde mi? (Bu alanlar çok airdrop yapar).
4. TVL (Kilitli Değer) İvmesi: Son 7 günde TVL'si %20'den fazla artmış mı?
5. Fırsat Türü: Bu bir Binance Launchpool'u mu, bir Galxe/Zealy görevi mi, yoksa Node/Testnet kurulumu mu?

Çıktı Formatın KESİNLİKLE şu şekilde bir JSON olmalıdır:
[
  {
    "project_name": "Proje Adı",
    "opportunity_type": "DeFi / Launchpool / Testnet / Social Quest",
    "airdrop_score": 85,
    "action_plan": "1. Siteye git, 2. Cüzdan bağla",
    "reasoning": "Kısa ve net analiz"
  }
]
Sadece 'airdrop_score' değeri 75 ve üzeri olanları döndür. Eğer verilen listede 75 puanı geçen proje yoksa KESİNLİKLE sadece boş bir JSON array yani [] döndür. Asla uydurma (halüsinasyon) veri üretme. Başka hiçbir açıklama metni yazma.
"""

def analyze_opportunities(projects):
    if not projects:
        return []

    # API Anahtarını GitHub Secrets'tan alıyor
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # AI'a incelenecek projeleri metin olarak veriyoruz
    user_content = f"İşte bugün radarımıza takılan projeler. Lütfen analiz et:\n{json.dumps(projects, indent=2)}"

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            model="llama3-70b-8192", # Veya kullandığın hangi modelse (mixtral-8x7b-32768 vb.)
            temperature=0.1, # Düşük sıcaklık = Daha az halüsinasyon, daha net mantık
        )

        ai_response = response.choices[0].message.content.strip()

        # Markdown formatında (```json ... ```) döndürdüyse o kısımları temizliyoruz ki Python hata vermesin
        if ai_response.startswith("```json"):
            ai_response = ai_response[7:]
        if ai_response.startswith("```"):
            ai_response = ai_response[3:]
        if ai_response.endswith("```"):
            ai_response = ai_response[:-3]

        # Temizlenmiş metni JSON'a (Python Listesine) çeviriyoruz
        return json.loads(ai_response.strip())

    except Exception as e:
        print(f"AI Analizinde bir hata oluştu: {e}")
        return []
