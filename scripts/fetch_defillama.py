import requests

from scripts.utils import clean_text


EXCLUDED_CATEGORIES = {
    "cex",
    "bridge",
    "indexes"
}


EXCLUDED_KEYWORDS = {
    "binance",
    "bybit",
    "coinbase",
    "bitfinex",
    "kraken",
    "robinhood",
    "okx",
    "kucoin",
    "htx",
    "bitget",
    "gemini",
    "wrapped"
}


def is_excluded(protocol):
    name = clean_text(
        protocol.get("name")
    ).lower()

    category = clean_text(
        protocol.get("category")
    ).lower()

    if category in EXCLUDED_CATEGORIES:
        return True

    for keyword in EXCLUDED_KEYWORDS:
        if keyword in name:
            return True

    return False


def fetch_defillama_candidates(
    limit=30
):
    print(
        "DeFiLlama protokolleri taranıyor..."
    )

    url = (
        "https://api.llama.fi/protocols"
    )

    response = requests.get(
        url,
        timeout=20
    )

    response.raise_for_status()

    protocols = response.json()

    candidates = []

    for protocol in protocols:

        if is_excluded(protocol):
            continue

        tvl = float(
            protocol.get("tvl")
            or 0
        )

        # Eski sistemde 500M USD idi.
        # Discovery için fazla yüksekti.
        if tvl < 5_000_000:
            continue

        name = clean_text(
            protocol.get("name")
        )

        symbol = clean_text(
            protocol.get("symbol")
        )

        category = clean_text(
            protocol.get("category")
        )

        chain = clean_text(
            protocol.get("chain")
        )

        project_url = (
            protocol.get("url")
            or ""
        )

        description = (
            f"DeFi protokolü. "
            f"Kategori: "
            f"{category or 'bilinmiyor'}. "
            f"TVL: ${tvl:,.0f}. "
            f"Chain: "
            f"{chain or 'bilinmiyor'}. "
            f"DeFiLlama symbol alanı: "
            f"{symbol or 'bilinmiyor'}."
        )

        candidate = {
            "project_name": name,

            "url": project_url,

            "description": (
                description
            ),

            "source": "DeFiLlama",

            "source_type": (
                "protocol_discovery"
            ),

            "tvl_usd": round(tvl),

            "chain": (
                chain
                or None
            ),

            "category": (
                category
                or None
            ),

            # ÖNEMLİ:
            # Bu alan tokenın gerçekten
            # piyasada olduğu anlamına gelmez.
            "defillama_symbol": (
                symbol
                or None
            )
        }

        candidates.append(
            candidate
        )

    candidates.sort(
        key=lambda item: (
            item.get(
                "tvl_usd",
                0
            )
        ),
        reverse=True
    )

    candidates = (
        candidates[:limit]
    )

    print(
        f"DeFiLlama: "
        f"{len(candidates)} "
        f"aday bulundu."
    )

    return candidates
