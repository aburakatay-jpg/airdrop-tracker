import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from scripts.utils import (
    clean_text,
    domain_of
)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(compatible; AirdropRadar/2.0; "
        "+personal-research)"
    )
}


IMPORTANT_TERMS = [
    "airdrop",
    "points",
    "point",
    "season",
    "epoch",
    "quest",
    "testnet",
    "faucet",
    "reward",
    "rewards",
    "token",
    "tge",
    "snapshot",
    "claim",
    "mainnet",
    "campaign",
    "xp",
    "genesis"
]


def fetch_page_context(url):
    if not url:
        return {
            "page_ok": False,
            "page_text": "",
            "page_title": "",
            "links": []
        }

    if not url.startswith(
        ("http://", "https://")
    ):
        return {
            "page_ok": False,
            "page_text": "",
            "page_title": "",
            "links": []
        }

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15,
            allow_redirects=True
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Gereksiz içerikleri kaldır
        for tag in soup(
            [
                "script",
                "style",
                "noscript",
                "svg"
            ]
        ):
            tag.decompose()

        # Sayfa başlığı
        if soup.title:
            page_title = clean_text(
                soup.title.get_text(
                    " ",
                    strip=True
                )
            )
        else:
            page_title = ""

        # Sayfanın bütün metni
        full_text = clean_text(
            soup.get_text(
                " ",
                strip=True
            )
        )

        # Airdrop ile ilgili paragrafları
        # özellikle toplamaya çalış
        important_chunks = []

        for node in soup.find_all(
            [
                "p",
                "li",
                "h1",
                "h2",
                "h3",
                "h4"
            ]
        ):
            text = clean_text(
                node.get_text(
                    " ",
                    strip=True
                )
            )

            if not text:
                continue

            lower_text = text.lower()

            relevant = any(
                term in lower_text
                for term in IMPORTANT_TERMS
            )

            if relevant:
                important_chunks.append(
                    text
                )

        selected_text = " ".join(
            important_chunks
        )

        # Çok az ilgili metin bulunduysa,
        # sayfanın ilk bölümünü kullan.
        if len(selected_text) < 500:
            selected_text = (
                full_text[:7000]
            )
        else:
            selected_text = (
                selected_text[:7000]
            )

        # Linkleri de çıkar
        links = []

        base_domain = domain_of(
            response.url
        )

        for anchor in soup.find_all(
            "a",
            href=True
        ):
            href = anchor.get(
                "href"
            )

            if not href:
                continue

            absolute_url = urljoin(
                response.url,
                href
            )

            if not absolute_url.startswith(
                ("http://", "https://")
            ):
                continue

            link_text = clean_text(
                anchor.get_text(
                    " ",
                    strip=True
                )
            )

            same_domain = (
                domain_of(
                    absolute_url
                )
                == base_domain
            )

            links.append({
                "text": (
                    link_text[:120]
                ),

                "url": (
                    absolute_url
                ),

                "same_domain": (
                    same_domain
                )
            })

        return {
            "page_ok": True,

            "resolved_url": (
                response.url
            ),

            "page_title": (
                page_title
            ),

            "page_text": (
                selected_text
            ),

            "links": (
                links[:80]
            )
        }

    except Exception as e:
        return {
            "page_ok": False,

            "page_text": "",

            "page_title": "",

            "links": [],

            "page_error": (
                str(e)
            )
        }


def enrich_candidate(
    candidate
):
    enriched = dict(
        candidate
    )

    project_url = (
        candidate.get("url")
        or ""
    )

    context = fetch_page_context(
        project_url
    )

    enriched[
        "web_context"
    ] = context

    return enriched
