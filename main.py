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
from scripts.notify import (
    send_message,
    format_airdrop_message
)
from scripts.storage import (
    was_seen,
    mark_seen,
    save_project_state,
    load_web_items,
    save_web_items
)
from scripts.utils import (
    today_str,
    candidate_id
)


def collect_candidates():
    collected = []

    # Burada mümkün olduğunca geniş bir aday havuzu
    # topluyoruz.
    #
    # MAX_CANDIDATES_PER_RUN sınırını burada
    # uygulamıyoruz.
    #
    # Önce seen projeleri eleyeceğiz,
    # sonra çalışma başına limiti uygulayacağız.

    collectors = [
        (
            "DeFiLlama",
            lambda: fetch_defillama_candidates(
                limit=200
            )
        ),

        (
            "Airdrops.io",
            lambda: fetch_airdrops_io(
                limit=50
            )
        ),

        (
            "Exchange News",
            lambda: fetch_exchange_news(
                limit=30
            )
        ),
    ]

    for name, collector in collectors:
        try:
            items = collector() or []

            print(
                f"{name}: "
                f"{len(items)} aday"
            )

            collected.extend(
                items
            )

        except Exception as e:
            print(
                f"{name} collector hatası: "
                f"{e}"
            )

    # Duplicate temizliği.
    #
    # URL/project name yerine candidate_id
    # kullanıyoruz.
    unique = {}

    for item in collected:
        project_id = candidate_id(
            item
        )

        if project_id not in unique:
            unique[
                project_id
            ] = item

    candidates = list(
        unique.values()
    )

    print("")
    print(
        "Duplicate temizliği sonrası "
        f"aday: {len(candidates)}"
    )

    return candidates


def select_new_candidates(
    candidates
):
    new_items = []

    seen_count = 0

    for item in candidates:

        if was_seen(item):
            seen_count += 1
            continue

        # Projenin kimliğini pipeline
        # boyunca koruyoruz.
        item[
            "_candidate_id"
        ] = candidate_id(
            item
        )

        new_items.append(
            item
        )

    print(
        f"Daha önce görülen: "
        f"{seen_count}"
    )

    print(
        f"Yeni bulunan: "
        f"{len(new_items)}"
    )

    # En önemli değişiklik:
    #
    # Limiti seen filtresinden SONRA
    # uyguluyoruz.
    return new_items[
        :MAX_CANDIDATES_PER_RUN
    ]


def enrich_candidates(
    candidates
):
    enriched = []

    for i, item in enumerate(
        candidates,
        start=1
    ):

        print(
            f"Enrichment "
            f"{i}/{len(candidates)}: "
            f"{item.get('project_name')}"
        )

        try:
            enriched_item = (
                enrich_candidate(
                    item
                )
            )

            # candidate ID kaybolmasın.
            enriched_item[
                "_candidate_id"
            ] = item.get(
                "_candidate_id"
            )

            enriched.append(
                enriched_item
            )

        except Exception as e:

            copy = dict(
                item
            )

            copy[
                "enrichment_error"
            ] = str(e)

            enriched.append(
                copy
            )

    return enriched


def classify_for_delivery(
    item
):
    airdrop_score = int(
        item.get(
            "airdrop_score"
        )
        or 0
    )

    free_score = int(
        item.get(
            "free_score"
        )
        or 0
    )

    zero_cost = bool(
        item.get(
            "zero_cost_confirmed"
        )
    )

    # Kullanıcı para yatırmadan
    # fırsat arıyor.

    if item.get(
        "requires_deposit"
    ):
        return "REJECT"

    if item.get(
        "requires_purchase"
    ):
        return "REJECT"

    if item.get(
        "requires_trading_volume"
    ):
        return "REJECT"

    # Güçlü ücretsiz fırsat
    if (
        zero_cost
        and free_score >= MIN_FREE_SCORE
        and airdrop_score >= MIN_AIRDROP_SCORE
    ):
        return "PRIORITY"

    # Ücretsiz ama henüz yeterince
    # güçlü olmayan fırsat
    if (
        zero_cost
        and airdrop_score >= 35
    ):
        return "WATCH"

    return "REJECT"


def main():
    print("")
    print(
        "======================================"
    )
    print(
        "Airdrop Radar V2 başlıyor..."
    )
    print(
        "======================================"
    )
    print("")

    # ---------------------------------
    # 1. ADAY HAVUZUNU TOPLA
    # ---------------------------------

    raw_candidates = (
        collect_candidates()
    )

    print("")
    print(
        f"Toplam ham aday havuzu: "
        f"{len(raw_candidates)}"
    )

    # ---------------------------------
    # 2. SEEN PROJELERİ ÇIKAR
    # ---------------------------------

    new_candidates = (
        select_new_candidates(
            raw_candidates
        )
    )

    if not new_candidates:

        print("")
        print(
            "Bu çalışmada yeni aday yok."
        )

        print(
            "Sistem tamamlandı."
        )

        return

    print("")
    print(
        "Bu çalışmada analiz edilecek "
        f"aday: {len(new_candidates)}"
    )

    # ---------------------------------
    # 3. WEB ENRICHMENT
    # ---------------------------------

    enriched_candidates = (
        enrich_candidates(
            new_candidates
        )
    )

    # ---------------------------------
    # 4. AI ANALİZİ
    # ---------------------------------

    batch_size = 10

    analyzed_results = []

    failed_batches = []

    for start in range(
        0,
        len(enriched_candidates),
        batch_size
    ):

        batch = (
            enriched_candidates[
                start:
                start + batch_size
            ]
        )

        print("")
        print(
            "AI batch analiz: "
            f"{start + 1}-"
            f"{start + len(batch)}"
        )

        try:

            batch_results = (
                analyze_candidates(
                    batch
                )
            )

            if (
                batch_results
                and isinstance(
                    batch_results,
                    list
                )
            ):
                analyzed_results.extend(
                    batch_results
                )

        except Exception as e:

            print(
                f"AI batch hatası: "
                f"{e}"
            )

            # Bu adayları seen yapmıyoruz.
            #
            # Sonraki çalışmada tekrar
            # denenecekler.
            failed_batches.extend(
                batch
            )

    # ---------------------------------
    # 5. ERROR KAYITLARI
    # ---------------------------------

    for failed in failed_batches:

        error_project = dict(
            failed
        )

        error_project[
            "pipeline_status"
        ] = "ERROR"

        save_project_state(
            error_project
        )

    # AI hiç sonuç üretmediyse
    # seen kayıtlarını değiştirme.
    if not analyzed_results:

        print("")
        print(
            "AI analiz sonucu üretmedi."
        )

        print(
            "Projeler seen yapılmadı."
        )

        print(
            "Sonraki çalışmada "
            "tekrar denenecek."
        )

        return

    # ---------------------------------
    # 6. WEB'DEKİ ESKİ KAYITLAR
    # ---------------------------------

    existing_web_items = (
        load_web_items()
    )

    publishable_items = []

    # ---------------------------------
    # 7. SONUÇLARI SINIFLANDIR
    # ---------------------------------

    for result in analyzed_results:

        result[
            "status"
        ] = classify_for_delivery(
            result
        )

        result[
            "date_added"
        ] = today_str()

        # Proje state kaydı
        save_project_state(
            result
        )

        # PRIORITY + WATCH
        # web sitesinde gösterilir.
        if result[
            "status"
        ] in {
            "PRIORITY",
            "WATCH"
        }:

            publishable_items.append(
                result
            )

        # Telegram'a yalnızca
        # güçlü fırsatlar gider.
        if (
            result["status"]
            == "PRIORITY"
        ):

            telegram_message = (
                format_airdrop_message(
                    result
                )
            )

            send_message(
                telegram_message
            )

        # AI başarılı şekilde analiz
        # ettiyse seen yap.
        mark_seen(
            result,
            status=result[
                "status"
            ]
        )

    # ---------------------------------
    # 8. WEB JSON GÜNCELLE
    # ---------------------------------

    if publishable_items:

        save_web_items(
            existing_web_items
            + publishable_items
        )

    # ---------------------------------
    # 9. RUN ÖZETİ
    # ---------------------------------

    priority_count = sum(
        1
        for item in analyzed_results
        if item.get(
            "status"
        ) == "PRIORITY"
    )

    watch_count = sum(
        1
        for item in analyzed_results
        if item.get(
            "status"
        ) == "WATCH"
    )

    reject_count = sum(
        1
        for item in analyzed_results
        if item.get(
            "status"
        ) == "REJECT"
    )

    print("")
    print(
        "======================================"
    )
    print(
        "İŞLEM TAMAMLANDI"
    )
    print(
        "======================================"
    )

    print(
        f"PRIORITY : "
        f"{priority_count}"
    )

    print(
        f"WATCH    : "
        f"{watch_count}"
    )

    print(
        f"REJECT   : "
        f"{reject_count}"
    )

    print(
        f"ERROR    : "
        f"{len(failed_batches)}"
    )

    print(
        "======================================"
    )


if __name__ == "__main__":
    main()
