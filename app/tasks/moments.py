from datetime import date, timedelta

OPEN_GROUPS = (
    ("overdue", "En retard"),
    ("today", "Aujourd'hui"),
    ("tomorrow", "Demain"),
    ("week", "Dans les 7 jours"),
    ("later", "Plus tard"),
    ("someday", "Sans échéance"),
)
DONE_GROUPS = (
    ("today", "Terminées aujourd'hui"),
    ("week", "Cette semaine"),
    ("earlier", "Plus tôt"),
)


def day_start(offset=0):
    return f"{date.today() + timedelta(days=offset):%Y-%m-%d}T00:00"


def days_from_today(timestamp):
    return (date.fromisoformat(timestamp[:10]) - date.today()).days


def due_group(due_at):
    if not due_at:
        return "someday"
    days = days_from_today(due_at)
    if days < 0:
        return "overdue"
    return {0: "today", 1: "tomorrow"}.get(days, "week" if days <= 7 else "later")


def done_group(completed_at):
    days = -days_from_today(completed_at) if completed_at else 7
    return "today" if days == 0 else "week" if days < 7 else "earlier"


def group_tasks(tasks, view):
    if view == "done":
        groups, key_of = DONE_GROUPS, lambda task: done_group(task["completed_at"])
    else:
        groups, key_of = OPEN_GROUPS, lambda task: due_group(task["due_at"])
    buckets = {key: [] for key, _ in groups}
    for task in tasks:
        buckets[key_of(task)].append(task)
    return [(key, label, buckets[key]) for key, label in groups if buckets[key]]
