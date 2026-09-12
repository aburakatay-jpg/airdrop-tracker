import json
import re

from groq import Groq

from config import GROQ_API_KEY

from scripts.utils import (
    candidate_id,
    clean_text
)


SYSTEM_PROMPT = """
Sen kıdemli bir Web3 araştırmacısı,
airdrop analisti ve güvenlik filtresisin.

AMAÇ:

Kullanıcı para yatırmadan,
token/NFT satın almadan veya
zorunlu trading hacmi oluşturmadan
katılabileceği:

- Airdrop
- Testnet
- Points
- Quest
- Faucet
- Early user

fırsatlarını arıyor.

TEMEL KURAL:

Bu sistemin önceliği
"bedava veya gerçekten sıfıra yakın maliyetle
katılabilecek fırsatlar"dır.


ÇOK ÖNEMLİ KURALLAR:

1.
Sana verilmemiş bilgileri
kesinmiş gibi uydurma.

2.
Kaynak veya bilgi belirsizse
confidence_score düşür.

3.
Seed phrase,
private key,
recovery phrase

isteyen hiçbir işlemi önerme.

4.
Deposit gerekiyorsa:

requires_deposit = true
zero_cost_confirmed = false

5.
Token veya NFT satın almak gerekiyorsa:

requires_purchase = true
zero_cost_confirmed = false

6.
Trading volume gerekiyorsa:

requires_trading_volume = true
zero_cost_confirmed = false

7.
Mainnet üzerinde gerçek gas ücreti
gerekiyorsa bunu tamamen ücretsiz kabul etme.

8.
Tahmini maliyet bilinmiyorsa:

estimated_cost_usd = null

kullan.

9.
"Airdrop kesin gelecek"
gibi ifadeler kullanma.

Bunun yerine:

- ihtimal
- sinyal
- olasılık
- kanıt
- doğrulanmış kampanya

gibi ifadeler kullan.

10.
Aggregator bilgisi tek başına
resmi doğrulama değildir.

11.
Adım adım katılım rehberi
MUTLAKA üret.

12.
URL veya işlem doğrulanamıyorsa
bunu açıkça belirt.

13.
Ücretsiz testnet,
faucet,
social quest,
points campaign,
XP campaign

gibi fırsatlara daha yüksek
free_score ver.

14.
Proje hakkında yeterli kanıt yoksa
uydurmak yerine:

WATCH

veya

ERROR

kullan.

15.
Gerçek para yatırılması gerekiyorsa
PRIORITY verme.

16.
Resmi URL konusunda emin değilsen
null kullan.

17.
Bir linki official_url olarak vermeden önce
mevcut veride bunun gerçekten
resmi olduğuna dair makul kanıt ara.

18.
Kullanıcı için katılım adımlarını
mümkün olduğunca uygulanabilir yaz.

Örnek:

1. Projenin resmi alan adını doğrula.
2. Testnet sayfasına gir.
3. Yeni veya düşük bakiyeli bir cüzdan bağla.
4. Faucet varsa ücretsiz test tokenı al.
5. İstenen testnet görevini tamamla.
6. Dashboard üzerinden XP/Points işlendiğini kontrol et.
7. Yeni görevleri düzenli kontrol et.

PUANLAMA:

airdrop_score:

Airdrop veya gelecekte reward alma
ihtimali ve fırsat kalitesi.

0-100.

free_score:

Sermaye yatırmadan
katılabilme seviyesi.

0-100.

Deposit,
purchase veya trading gerekiyorsa
genellikle 0-30 aralığında olmalı.

confidence_score:

Eldeki verilerin güvenilirliği.

0-100.


STATUS:

PRIORITY:
Güçlü,
ücretsiz
ve yeterince doğrulanmış fırsat.

WATCH:
Umut verici
fakat kanıt eksik.

REJECT:
Ücretli,
uygunsuz
veya çok zayıf fırsat.

ERROR:
Sağlıklı değerlendirilemedi.


TOKEN STATUS:

no_token
announced
pre_tge
live
unknown


RISK LEVEL:

LOW
MEDIUM
HIGH


SADECE GEÇERLİ JSON ARRAY DÖNDÜR.

Markdown kullanma.

Code block kullanma.

Başka açıklama yazma.


HER PROJE İÇİN:

[
  {
    "project_name": "Proje adı",

    "opportunity_type":
    "Testnet | Points | Quest | Airdrop | Launchpool | Other",

    "status":
    "PRIORITY | WATCH | REJECT | ERROR",

    "airdrop_score": 0,

    "free_score": 0,

    "confidence_score": 0,

    "zero_cost_confirmed": true,

    "estimated_cost_usd": 0,

    "requires_deposit": false,

    "requires_purchase": false,

    "requires_trading_volume": false,

    "token_status":
    "no_token | announced | pre_tge | live | unknown",

    "reasoning":
    "Kısa fakat somut değerlendirme",

    "why_now":
    "Bu fırsat neden şimdi takip edilmeli?",

    "risk_level":
    "LOW | MEDIUM | HIGH",

    "risks": [
      "Risk 1",
      "Risk 2"
    ],

    "action_plan_steps": [
      "1. Adım",
      "2. Adım",
      "3. Adım"
    ],

    "verification_checklist": [
      "Resmi site doğrulandı mı?",
      "Cüzdan onayı ne istiyor?",
      "Seed phrase/private key isteniyor mu?"
    ],

    "official_url": null,

    "source_notes": [
      "Değerlendirmenin dayandığı kanıt"
    ]
  }
]
"""


def extract_json(text):
    if not text:
        raise ValueError(
            "AI boş cevap döndürdü."
        )

    text = text.strip()

    if text.startswith("```"):
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text
        )

        text = re.sub(
            r"\s*```$",
            "",
            text
        )

    return json.loads(text)


def analyze_candidates(candidates):
    if not candidates:
        return []

    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY tanımlı değil."
        )

    prepared_candidates = []

    for candidate in candidates:
        prepared = dict(candidate)

        prepared[
            "_candidate_id"
        ] = candidate_id(candidate)

        prepared_candidates.append(
            prepared
        )

    client = Groq(
        api_key=GROQ_API_KEY
    )

    user_payload = {
        "instruction": (
            "Aşağıdaki adayları yalnızca "
            "verilen kanıtlara göre değerlendir. "
            "Her aday için uygulanabilir, "
            "adım adım katılım planı üret."
        ),

        "candidates":
        prepared_candidates
    }

    response = (
        client
        .chat
        .completions
        .create(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        user_payload,
                        ensure_ascii=False
                    )
                }
            ],

            model=(
                "llama-3.3-70b-versatile"
            ),

            temperature=0.05
        )
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    data = extract_json(
        content
    )

    if not isinstance(
        data,
        list
    ):
        raise ValueError(
            "AI cevabı JSON array değil."
        )

    # AI'nin proje kimliğini kaybetmesini
    # engellemek için sonuçları
    # kaynak adaylarla yeniden eşleştiriyoruz.
    source_map = {}

    for candidate in prepared_candidates:
        name = clean_text(
            candidate.get(
                "project_name"
            )
        ).lower()

        if name:
            source_map[name] = {
                "_candidate_id":
                    candidate.get(
                        "_candidate_id"
                    ),

                "source_url":
                    candidate.get(
                        "url"
                    ),

                "source":
                    candidate.get(
                        "source"
                    )
            }

    for result in data:
        if not isinstance(
            result,
            dict
        ):
            continue

        result_name = clean_text(
            result.get(
                "project_name"
            )
        ).lower()

        source_info = (
            source_map.get(
                result_name
            )
        )

        if source_info:
            result[
                "_candidate_id"
            ] = source_info[
                "_candidate_id"
            ]

            result[
                "source_url"
            ] = source_info[
                "source_url"
            ]

            result[
                "source"
            ] = source_info[
                "source"
            ]

    return [
        item
        for item in data
        if isinstance(
            item,
            dict
        )
    ]
