import feedparser

from bs4 import BeautifulSoup

from scripts.utils import clean_text


def fetch_exchange_news(
    limit=15
):
    print(
        "Exchange haberleri taranıyor..."
    )

    rss_url = (
        "https://cointelegraph.com/"
        "rss/tag/binance"
    )

    feed = feedparser.parse(
        rss_url
    )

    keywords = [
        "launchpool",
        "megadrop",
        "airdrop",
        "launchpad",
        "giveaway",
        "reward",
        "alpha points",
        "tge"
    ]

    results = []

    for entry in feed.entries[:limit]:

        title = clean_text(
            getattr(
                entry,
                "title",
                ""
            )
        )

        summary_html = getattr(
            entry,
            "summary",
            ""
        )

        summary_text = (
            BeautifulSoup(
                summary_html,
                "html.parser"
            )
            .get_text(
                " ",
                strip=True
            )
        )

        summary_text = clean_text(
            summary_text
        )

        haystack = (
            f"{title} "
            f"{summary_text}"
        ).lower()

        is_relevant = any(
            keyword in haystack
            for keyword in keywords
        )

        if not is_relevant:
            continue

        result = {
            "project_name": title,

            "url": getattr(
                entry,
                "link",
                ""
            ),

            "description": (
                summary_text[:800]
            ),

            "source": (
                "Exchange News"
            ),

            "source_type": "news"
        }

        results.append(
            result
        )

    print(
        f"Exchange News: "
        f"{len(results)} "
        f"aday bulundu."
    )

    return results
