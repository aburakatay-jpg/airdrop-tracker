import json
import os
from datetime import datetime

# Tüm toplayıcıları ve araçları içe aktarıyoruz
from scripts.fetch_defillama import fetch_protocols
from scripts.fetch_binance import fetch_binance_opportunities
from scripts.fetch_socials import fetch_airdrop_sites
from scripts.groq_analyze import analyze_opportunities
from scripts.notify import send_message

def load_seen_data():
    try:
        with open("data/seen.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_seen_data(seen_list):
    os.makedirs("data", exist_ok=True)
    with open("data/seen.json", "w") as f:
        json.dump(seen_list, f, ensure_ascii=False, indent=2)

def save_for_web(new_approved_airdrops):
    os.makedirs("docs", exist_ok=True)
    file_path = "docs/airdrops.json"
    
    # Eski verileri oku
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
        
    # Yeni projeleri ekle (tarih damgası ile)
    for opp in new_approved_airdrops:
        opp['date_added'] = datetime.now().strftime("%Y-%m-%d")
        data.append(opp)
        
    # Puanlara göre yüksekten düşüğe sırala
    data = sorted(data, key=lambda x: x.get('airdrop_score', 0), reverse=True)
    
    # Dosyaya geri yaz
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print("Airdrop Radar başlatılıyor (Seviye 2 - Gruplu Analiz)...")
    seen_data = load_seen_data()
    all_raw_opportunities = []

    # 1. Verileri Topla
    try:
        all_raw_opportunities.extend(fetch_protocols())
    except Exception as e:
        print(f"DefiLlama hatası: {e}")

    try:
        all_raw_opportunities.extend(fetch_binance_opportunities())
    except Exception as e:
        print(f"Binance hatası: {e}")

    try:
        all_raw_opportunities.extend(fetch_airdrop_sites())
    except Exception as e:
        print(f"Airdrop siteleri hatası: {e}")

   # 2. Daha önce görülenleri ve alakasızları filtrele
    new_opportunities = []
    keywords = ["airdrop", "launchpool", "testnet", "reward", "quest", "points", "season", "drop"]
    
    for opp in all_raw_opportunities:
        unique_id = opp.get("url", opp.get("project_name")) 
        if unique_id not in seen_data:
            # Gelen değerlerin None olma ihtimaline karşı str() içine alarak güvene alıyoruz
            p_name = str(opp.get("project_name") or "")
            p_desc = str(opp.get("description") or "")
            
            text_to_check = (p_name + " " + p_desc).lower()
            
            # Eğer DefiLlama'dan gelen büyük bir protokolse veya içinde anahtar kelime varsa kabul et
            if opp.get("source") != "DefiLlama" or any(kw in text_to_check for kw in keywords):
                new_opportunities.append(opp)

    # Çok fazla aday varsa (örn: 50'den fazla), sadece en popüler/yeni ilk 40 tanesini al ki sistem uçmasın
    new_opportunities = new_opportunities[:40] 

    if not new_opportunities:
        print("Bugün radarımızda yeni aday bulunamadı.")
        send_message("Airdrop Radar - Bugün yeni fırsat bulunamadı.")
        return

    print(f"Filtrelemeden geçen {len(new_opportunities)} aday AI analizine gönderiliyor...")
    
    # Tek seferde temizce analiz et
    analyzed_results = analyze_opportunities(new_opportunities)

    # 3. 20'şerli Gruplar Halinde AI Analizi (Token Sınırını Aşmamak İçin)
    batch_size = 20 
    all_analyzed_results = []
    
    for i in range(0, len(new_opportunities), batch_size):
        batch = new_opportunities[i:i + batch_size]
        print(f"Grup {i//batch_size + 1} analiz ediliyor...")
        
        batch_results = analyze_opportunities(batch)
        if batch_results and isinstance(batch_results, list):
            all_analyzed_results.extend(batch_results)

    if not all_analyzed_results:
        print("AI hiçbir projeyi yeterince kaliteli bulmadı.")
        send_message("Airdrop Radar - Yeni projeler bulundu ancak AI onayından geçemedi (Puan < 75).")
        
        # Spam olmaması için tarananları seen.json'a ekle
        for opp in new_opportunities:
            unique_id = opp.get("url", opp.get("project_name"))
            if unique_id:
                seen_data.append(unique_id)
        save_seen_data(seen_data)
        return

    # 4. Puanı 75 ve üzeri olanları seç, Telegram'a at ve web için hazırla
    approved_airdrops = []
    
    for result in all_analyzed_results:
        score = result.get("airdrop_score", 0)
        if score >= 75:
            approved_airdrops.append(result)
            
            # Telegram Mesajı
            msg = f"🚀 YENİ FIRSAT YAKALANDI!\n\n"
            msg += f"🔥 Proje: {result.get('project_name')}\n"
            msg += f"🎯 Tür: {result.get('opportunity_type')}\n"
            msg += f"⭐ AI Puanı: {score}/100\n"
            msg += f"💡 Neden: {result.get('reasoning')}\n"
            msg += f"🛠 Aksiyon: {result.get('action_plan')}\n"
            send_message(msg)

    # 5. Eğer onaylanan varsa GitHub Pages (JSON) dosyasına kaydet
    if approved_airdrops:
        save_for_web(approved_airdrops)
        print(f"{len(approved_airdrops)} adet yüksek puanlı airdrop web sitesine eklendi.")

    # 6. İncelenen tüm yeni projeleri seen.json'a ekle (Tekrar tekrar bildirim gelmesin)
    for opp in new_opportunities:
        unique_id = opp.get("url", opp.get("project_name"))
        if unique_id:
            seen_data.append(unique_id)
            
    save_seen_data(seen_data)
    print("İşlem başarıyla tamamlandı, veriler kaydedildi.")

if __name__ == "__main__":
    main()
