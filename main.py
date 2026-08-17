import json
import os
# Tüm toplayıcıları içe aktarıyoruz
from scripts.fetch_defillama import fetch_protocols
from scripts.fetch_binance import fetch_binance_opportunities
from scripts.fetch_socials import fetch_airdrop_sites
from scripts.groq_analyze import analyze_opportunities
from scripts.notify import send_message # (veya send_notification, dosyadaki adına göre)

def load_seen_data():
    try:
        with open("data/seen.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_seen_data(seen_list):
    # Eğer data klasörü yoksa oluştur
    os.makedirs("data", exist_ok=True)
    with open("data/seen.json", "w") as f:
        json.dump(seen_list, f)

def main():
    print("Airdrop Radar başlatılıyor (Seviye 2)...")
    seen_data = load_seen_data()
    all_raw_opportunities = []

    # 1. DefiLlama
    all_raw_opportunities.extend(fetch_defillama_data())
    # 2. Binance/Borsalar
    all_raw_opportunities.extend(fetch_binance_opportunities())
    # 3. Airdrop Siteleri
    all_raw_opportunities.extend(fetch_airdrop_sites())

    # Daha önce gördüklerimizi filtrele (İsim veya URL bazlı)
    new_opportunities = []
    for opp in all_raw_opportunities:
        unique_id = opp.get("url", opp.get("project_name")) 
        if unique_id not in seen_data:
            new_opportunities.append(opp)

    if not new_opportunities:
        print("Yeni aday yok.")
        send_message("Airdrop Radar - Bugün yeni fırsat bulunamadı.")
        return

    print(f"{len(new_opportunities)} yeni proje/haber bulundu. Yapay Zeka inceliyor...")

    # AI Analizi
    analyzed_results = analyze_opportunities(new_opportunities)
    
    if not analyzed_results:
        print("AI hiçbir projeyi yeterince kaliteli bulmadı.")
        send_message("Airdrop Radar - Yeni projeler bulundu ancak AI onayından geçemedi (Puan < 75).")
        
        # Yine de spam olmaması için görülenleri kaydet
        for opp in new_opportunities:
            unique_id = opp.get("url", opp.get("project_name"))
            if unique_id:
                seen_data.append(unique_id)
        save_seen_data(seen_data)
        return

    # Onay alanları Telegrama gönder
    for result in analyzed_results:
        # Telegram mesajını şekillendir
        msg = f"🚀 YENİ FIRSAT YAKALANDI!\n\n"
        msg += f"🔥 Proje: {result.get('project_name')}\n"
        msg += f"🎯 Tür: {result.get('opportunity_type')}\n"
        msg += f"⭐ AI Puanı: {result.get('airdrop_score')}/100\n"
        msg += f"💡 Neden Seçildi: {result.get('reasoning')}\n"
        msg += f"🛠 Aksiyon Planı: {result.get('action_plan')}\n"
        
        send_message(msg)

    # Bildirilenleri arşive (seen.json) ekle
    for opp in new_opportunities:
        unique_id = opp.get("url", opp.get("project_name"))
        if unique_id:
            seen_data.append(unique_id)
            
    save_seen_data(seen_data)
    print("İşlem tamamlandı, kayıtlar güncellendi.")

if __name__ == "__main__":
    main()

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
    # ... (Veri çekme, filtreleme ve AI analiz kısımları aynı kalacak) ...

    # AI Analizi (Bu kısımdan sonrasını güncelliyoruz)
    analyzed_results = analyze_opportunities(new_opportunities)
    
    approved_airdrops = [] # Web'e gideceklerin listesi

    # Onay alanları Telegrama gönder ve listeye ekle
    for result in analyzed_results:
        if result.get("airdrop_score", 0) >= 75:
            approved_airdrops.append(result)
            
            # Telegram Mesajı
            msg = f"🚀 YENİ FIRSAT YAKALANDI!\n\n"
            msg += f"🔥 Proje: {result.get('project_name')}\n"
            msg += f"🎯 Tür: {result.get('opportunity_type')}\n"
            msg += f"⭐ AI Puanı: {result.get('airdrop_score')}/100\n"
            msg += f"🛠 Aksiyon: {result.get('action_plan')}\n"
            send_message(msg)

    # EĞER ONAYLANAN VARSA WEB SİTESİ İÇİN KAYDET
    if approved_airdrops:
        save_for_web(approved_airdrops)
