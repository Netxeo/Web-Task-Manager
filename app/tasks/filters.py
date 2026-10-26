from datetime import date, timedelta

from app.tasks.data.tags import normalize_tag

STATUSES = {"new": "Nouvelles", "scheduled": "Planifiées", "in_progress": "En cours", "done": "Terminées"}
PRIORITIES = {1: "Basse", 2: "Moyenne", 3: "Haute"}
VIEWS = {"board": "Kanban", "planner": "Planner"}
DEFAULTS = {"view": "board", "q": "", "tag": "", "priority": 0, "week": ""}
SEARCH_MAX_LENGTH = 100


def parse_priority(value):
    return int(value) if value in ("1", "2", "3") else 0


def parse_week(value):
    try:
        day = date.fromisoformat(value)
    except (TypeError, ValueError):
        return ""
    if not date(1, 1, 8) <= day <= date(9999, 12, 17):
        return ""
    return (day - timedelta(days=day.weekday())).isoformat()


def parse_filters(args):
    view = args.get("view", "")
    return {
        "view": view if view in VIEWS else DEFAULTS["view"],
        "q": " ".join(args.get("q", "").split())[:SEARCH_MAX_LENGTH],
        "tag": normalize_tag(args.get("tag", "")) or "",
        "priority": parse_priority(args.get("priority", "")),
        "week": parse_week(args.get("week", "")),
    }


def query_args(filters, **changes):
    merged = {**filters, **changes}
    return {key: value for key, value in merged.items() if value != DEFAULTS[key]}


def has_active_filters(filters):
    return any(filters[key] != DEFAULTS[key] for key in ("q", "tag", "priority"))
