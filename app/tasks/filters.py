from app.tasks.tags import normalize_tag

VIEWS = {"today": "Aujourd'hui", "upcoming": "À venir", "todo": "À faire", "done": "Terminées"}
PRIORITIES = {1: "Basse", 2: "Moyenne", 3: "Haute"}
SORTS = {
    "recent": ("Plus récentes", "t.created_at DESC"),
    "due": ("Échéance", "t.due_at IS NULL, t.due_at ASC, t.created_at DESC"),
    "priority": ("Priorité", "t.priority DESC, t.created_at DESC"),
    "title": ("Titre", "t.title COLLATE NOCASE ASC"),
}
DEFAULTS = {"view": "todo", "q": "", "tag": "", "priority": 0, "sort": "recent"}
SEARCH_MAX_LENGTH = 100


def parse_priority(value):
    return int(value) if value in ("1", "2", "3") else 0


def parse_filters(args):
    view = args.get("view", "")
    sort = args.get("sort", "")
    return {
        "view": view if view in VIEWS else DEFAULTS["view"],
        "q": " ".join(args.get("q", "").split())[:SEARCH_MAX_LENGTH],
        "tag": normalize_tag(args.get("tag", "")) or "",
        "priority": parse_priority(args.get("priority", "")),
        "sort": sort if sort in SORTS else DEFAULTS["sort"],
    }


def query_args(filters, **changes):
    merged = {**filters, **changes}
    return {key: value for key, value in merged.items() if value != DEFAULTS[key]}


def has_active_filters(filters):
    return any(filters[key] != DEFAULTS[key] for key in ("q", "tag", "priority"))
