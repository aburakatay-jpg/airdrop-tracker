import requests
import json
import os
from datetime import datetime

# Bu kategoriler ve isimler airdrop vermez, filtrele
EXCLUDED_CATEGORIES = ["CEX", "Bridge", "RWA", "Indexes"]
EXCLUDED_KEYWORDS = ["binance", "bybit", "coinbase", "bitfinex", "kraken", 
                     "robinhood", "okx", "kucoin", "htx", "bitget", "gemini",
                     "bridge", "wrapped", "staked", "liquid staking"]

def fetch_protocols():
    url = "https://api.llama.fi/protocols"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

def is_excluded(protocol):
    name = (protocol.get("name") or "").lower()
    category = (protocol.get("category") or "").lower()
    
    if category in [c.lower() for c in EXCLUDED_CATEGORIES]:
        return True
    
    for keyword in EXCLUDED_KEYWORDS:
        if keyword in name:
            return True
    
    return False

def filter_candidates(protocols):
    candidates = []
    
    for p in protocols:
        tvl = p.get("tvl") or 0
        has_token = p.get("symbol") not in [None, "", "-"]
        
        if tvl >= 500_000_000 and not has_token and not is_excluded(p):
            candidates.append({
                "name": p.get("name"),
                "symbol": p.get("symbol"),
                "tvl": round(tvl),
                "chain": p.get("chain"),
                "category": p.get("category"),
                "url": p.get("url"),
                "first_seen": datetime.now().isoformat()
            })
    
    # TVL'e göre sırala
    candidates.sort(key=lambda x: x["tvl"], reverse=True)
    return candidates

def load_seen():
    path = "data/seen.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_seen(seen):
    with open("data/seen.json", "w", encoding="utf-8") as f:
        json.dump(seen, f, indent=2, ensure_ascii=False)

def get_new_candidates():
    print("DefiLlama'dan protokoller çekiliyor...")
    protocols = fetch_protocols()
    candidates = filter_candidates(protocols)
    
    seen = load_seen()
    seen_names = {p["name"] for p in seen}
    
    new_ones = [c for c in candidates if c["name"] not in seen_names]
    
    if new_ones:
        seen.extend(new_ones)
        save_seen(seen)
        print(f"{len(new_ones)} yeni aday bulundu.")
    else:
        print("Yeni aday yok.")
    
    return new_ones

if __name__ == "__main__":
    # Test için seen.json'ı sıfırla
    if os.path.exists("data/seen.json"):
        os.remove("data/seen.json")
    
    results = get_new_candidates()
    print(f"\nToplam {len(results)} temiz aday:")
    for r in results:
        print(f"- {r['name']} | TVL: ${r['tvl']:,} | Kategori: {r['category']} | Zincir: {r['chain']}")