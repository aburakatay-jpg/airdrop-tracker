import json
import os

from config import (
    SEEN_FILE,
    STATE_FILE,
    WEB_FILE
)

from scripts.utils import candidate_id


def _load_json(path, default):
    try:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):
        return default


def _save_json(path, data):
    folder = os.path.dirname(path)

    if folder:
        os.makedirs(
            folder,
            exist_ok=True
        )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def load_seen():
    data = _load_json(
        SEEN_FILE,
        {}
    )

    if isinstance(data, dict):
        return data

    return {}


def was_seen(project):
    seen = load_seen()

    project_id = candidate_id(
        project
    )

    return project_id in seen


def mark_seen(
    project,
    status="analyzed"
):
    seen = load_seen()

    project_id = candidate_id(
        project
    )

    seen[project_id] = {
        "project_name": (
            project.get("project_name")
            or project.get("name")
            or "Unknown"
        ),

        "url": (
            project.get("url")
            or project.get("official_url")
            or ""
        ),

        "status": status
    }

    _save_json(
        SEEN_FILE,
        seen
    )


def load_project_state():
    data = _load_json(
        STATE_FILE,
        {}
    )

    if isinstance(data, dict):
        return data

    return {}


def save_project_state(project):
    state = load_project_state()

    project_id = candidate_id(
        project
    )

    state[project_id] = project

    _save_json(
        STATE_FILE,
        state
    )


def load_web_items():
    data = _load_json(
        WEB_FILE,
        []
    )

    if isinstance(data, list):
        return data

    return []


def save_web_items(items):
    unique_items = {}

    for item in items:
        key = (
            item.get("official_url")
            or item.get("url")
            or item.get("project_name")
        )

        if not key:
            continue

        unique_items[
            str(key).strip().lower()
        ] = item

    ordered_items = sorted(
        unique_items.values(),
        key=lambda item: (
            item.get("status") == "PRIORITY",
            int(
                item.get(
                    "airdrop_score",
                    0
                ) or 0
            ),
            int(
                item.get(
                    "free_score",
                    0
                ) or 0
            ),
            int(
                item.get(
                    "confidence_score",
                    0
                ) or 0
            )
        ),
        reverse=True
    )

    _save_json(
        WEB_FILE,
        ordered_items
    )
