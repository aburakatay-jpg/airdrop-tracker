import feedparser

from bs4 import BeautifulSoup

from scripts.utils import clean_text


def fetch_airdrops_io(limit=20):
    print("Airdrops.io RSS taranıyor...")

    rss_url = "https://airdrops.io/feed/"

    feed = feedparser.parse(
        rss_url
    )

    opportunities = []

    for entry in feed.entries[:limit]:

        title = clean_text(
            getattr(
                entry,
                "title",
                ""
            )
        )

        link = getattr(
            entry,
            "link",
            ""
        )

        summary_html = getattr(
            entry,
            "summary",
            ""
        )

        summary_text = BeautifulSoup(
            summary_html,
            "html.parser"
        ).get_text(
            " ",
            strip=True
        )

        summary_text = clean_text(
            summary_text
        )

        opportunity = {
            "project_name": title,

            "url": link,

            "description": (
                summary_text[:800]
            ),

            "source": "Airdrops.io",

            "source_type": "aggregator"
        }

        opportunities.append(
            opportunity
        )

    print(
        f"Airdrops.io: "
        f"{len(opportunities)} aday bulundu."
    )

    return opportunities
