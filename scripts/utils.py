from datetime import datetime, timezone
from urllib.parse import urlparse
import hashlib
import re


def now_iso():
    return datetime.now(
        timezone.utc
    ).isoformat()


def today_str():
    return datetime.now().strftime(
        "%Y-%m-%d"
    )


def clean_text(value):
    if value is None:
        return ""

    text = str(value)

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


def normalize_url(url):
    if not url:
        return ""

    url = str(url).strip()

    if not url.startswith(
        ("http://", "https://")
    ):
        return ""

    return url


def domain_of(url):
    try:
        return (
            urlparse(str(url))
            .netloc
            .lower()
            .replace("www.", "")
        )
    except Exception:
        return ""


def candidate_id(project):
    # Eğer proje daha önce pipeline içinde
    # kimlik aldıysa HER ZAMAN onu koru.
    existing_id = project.get(
        "_candidate_id"
    )

    if existing_id:
        return str(existing_id)

    base = (
        project.get("url")
        or project.get("official_url")
        or project.get("project_name")
        or project.get("name")
        or "unknown"
    )

    normalized_base = (
        str(base)
        .strip()
        .lower()
    )

    return hashlib.sha256(
        normalized_base.encode("utf-8")
    ).hexdigest()[:24]
