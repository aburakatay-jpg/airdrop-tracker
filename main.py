from config import (
    MIN_AIRDROP_SCORE,
    MIN_FREE_SCORE,
    MAX_CANDIDATES_PER_RUN
)

from scripts.fetch_airdropsio import fetch_airdrops_io
from scripts.fetch_defillama import fetch_defillama_candidates
from scripts.fetch_binance import fetch_exchange_news
from scripts.enrich import enrich_candidate
from scripts.analyze import analyze_candidates
from scripts.notify import send_message, format_airdrop_message
from scripts.storage import (
    was_seen,
    mark_seen,
    save_project_state,
    load_web_items,
    save_web_items
)
from scripts.utils import today_str


def collect_candidates():
    collected = []

    collectors = [
        ("DeFiLlama", lambda: fetch_defillama_candidates(limit=30)),
        ("Airdrops.io", lambda: fetch_airdrops_io(limit=20)),
        ("Exchange News", lambda: fetch_exchange_news(limit=15)),
    ]

    for name, collector in collectors:
        try:
            items = collector() or []
            print(f"{name}: {len(items)} aday")
            collected.extend(items)

        except Exception as e:
            print(f"{name} collector hatası: {e}")

    unique = {}

    for item in collected:
        key = (
            item.get("url")
            or item.get("project_name")
            or ""
        ).strip().lower()

        if key and key not in unique:
            unique[key] = item

    return list(unique.values())[:MAX_CANDIDATES_PER_RUN]


def select_new_candidates(candidates):
    new_items = []

    for item in candidates:
        if not was_seen(item):
            new_items.append(item)

    return new_items


def enrich_candidates(candidates):
    enriched = []

    for i, item in enumerate(candidates, start=1):
        print(
            f"Enrichment {i}/{len(candidates)}: "
            f"{item.get('project_name')}"
        )

        try:
            enriched.append(enrich_candidate(item))

        except Exception as e:
            copy = dict(item)
            copy["enrichment_error"] = str(e)
            enriched.append(copy)

    return enriched


def classify_for_delivery(item):
    airdrop_score = int(item.get("airdrop_score") or 0)
    free_score = int(item.get("free_score") or 0)
    zero_cost = bool(item.get("zero_cost_confirmed"))

    # Bizim ana hedefimiz:
    # PARA YATIRMADAN yapılabilecek fırsatlar.

    if item.get("requires_deposit"):
        return "REJECT"

    if item.get("requires_purchase"):
        return "REJECT"

    if item.get("requires_trading_volume"):
        return "REJECT"

    if (
        zero_cost
        and free_score >= MIN_FREE_SCORE
        and airdrop_score >= MIN_AIRDROP_SCORE
    ):
        return "PRIORITY"

    if zero_cost and airdrop_score >= 35:
        return "WATCH"

    return "REJECT"


def main():
    print("")
    print("======================================")
    print("Airdrop Radar V2 başlıyor...")
    print("======================================")
    print("")

    # 1. ADAYLARI TOPLA
    raw_candidates = collect_candidates()

    print("")
    print(f"Toplam ham aday: {len(raw_candidates)}")

    # 2. DAHA ÖNCE ANALİZ EDİLMEYENLERİ SEÇ
    new_candidates = select_new_candidates(raw_candidates)

    if not new_candidates:
        print("")
        print("Yeni aday yok.")
        print("Sistem tamamlandı.")
        return

    print("")
    print(f"{len(new_candidates)} yeni aday bulundu.")

    # 3. ADAYLARIN WEB SAYFALARINDAN EK BİLGİ TOPLA
    enriched_candidates = enrich_candidates(new_candidates)

    # 4. AI ANALİZİ
    # Token limiti ve hata riskini azaltmak için 10'lu gruplar.
    batch_size = 10

    analyzed_results = []
    failed_batches = []

    for start in range(
        0,
        len(enriched_candidates),
        batch_size
    ):
        batch = enriched_candidates[
            start:start + batch_size
        ]

        print("")
        print(
            f"AI batch analiz: "
            f"{start + 1}-"
            f"{start + len(batch)}"
        )

        try:
            batch_results = analyze_candidates(batch)

            if (
                batch_results
                and isinstance(batch_results, list)
            ):
                analyzed_results.extend(batch_results)

        except Exception as e:
            print(f"AI batch hatası: {e}")

            # AI hata verirse bu projeleri seen yapmıyoruz.
            # Sonraki çalışmada tekrar analiz edilecekler.
            failed_batches.extend(batch)

    # 5. AI HATASI ALANLARI ERROR OLARAK SAKLA
    for failed in failed_batches:
        error_project = dict(failed)
        error_project["pipeline_status"] = "ERROR"

        save_project_state(error_project)

    # Hiç sonuç gelmediyse projeleri seen yapmadan çık.
    if not analyzed_results:
        print("")
        print(
            "Analiz sonucu yok. "
            "Adaylar sonraki çalışmada tekrar denenecek."
        )
        return

    # 6. WEB'DEKİ ESKİ KAYITLARI OKU
    existing_web_items = load_web_items()

    publishable_items = []

    # 7. SONUÇLARI SINIFLANDIR
    for result in analyzed_results:

        result["status"] = classify_for_delivery(
            result
        )

        result["date_added"] = today_str()

        # Database/state kaydı
        save_project_state(result)

        # PRIORITY ve WATCH web sitesinde gösterilecek.
        if result["status"] in {
            "PRIORITY",
            "WATCH"
        }:
            publishable_items.append(result)

        # Yalnızca güçlü fırsatları Telegram'a gönder.
        if result["status"] == "PRIORITY":
            telegram_message = format_airdrop_message(
                result
            )

            send_message(telegram_message)

        # Sadece başarıyla AI analizinden geçenleri seen yap.
        mark_seen(
            result,
            status=result["status"]
        )

    # 8. WEB JSON DOSYASINI GÜNCELLE
    if publishable_items:
        save_web_items(
            existing_web_items
            + publishable_items
        )

    # 9. ÖZET
    priority_count = sum(
        1
        for item in analyzed_results
        if item.get("status") == "PRIORITY"
    )

    watch_count = sum(
        1
        for item in analyzed_results
        if item.get("status") == "WATCH"
    )

    reject_count = sum(
        1
        for item in analyzed_results
        if item.get("status") == "REJECT"
    )

    print("")
    print("======================================")
    print("İŞLEM TAMAMLANDI")
    print("======================================")
    print(f"PRIORITY : {priority_count}")
    print(f"WATCH    : {watch_count}")
    print(f"REJECT   : {reject_count}")
    print("======================================")


if __name__ == "__main__":
    main()