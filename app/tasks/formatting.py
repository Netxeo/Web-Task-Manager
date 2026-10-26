from datetime import date, datetime, timedelta
from urllib.parse import urlsplit

from app.tasks import bp
from app.tasks.filters import query_args
from app.tasks.forms import DUE_FORMAT

bp.add_app_template_global(query_args)

DAYS = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
MONTHS = ("janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc.")


def parse_due(value):
    return datetime.strptime(value, DUE_FORMAT)


@bp.app_template_filter("due_label")
def due_label(value):
    due = parse_due(value)
    days = (due.date() - date.today()).days
    names = {-1: "Hier", 0: "Aujourd'hui", 1: "Demain"}
    day = names.get(days, f"{due.day} {MONTHS[due.month - 1]}")
    if due.year != date.today().year and days not in names:
        day += f" {due.year}"
    return f"{day} · {due:%H:%M}"


@bp.app_template_test("overdue")
def is_overdue(task):
    return bool(task["due_at"]) and not task["is_done"] and parse_due(task["due_at"]) < datetime.now()


@bp.app_template_test("due_soon")
def is_due_soon(task):
    if not task["due_at"] or task["is_done"]:
        return False
    return datetime.now() <= parse_due(task["due_at"]) <= datetime.now() + timedelta(hours=24)


@bp.app_template_filter("day_label")
def day_label(day):
    return f"{DAYS[day.weekday()][:3].capitalize()} {day.day}"


@bp.app_template_filter("short_date")
def short_date(day):
    return f"{day.day} {MONTHS[day.month - 1]}"


@bp.app_template_test("today")
def is_today(day):
    return day == date.today()


@bp.app_template_filter("file_size")
def file_size(size):
    return f"{size / 1024:.0f} Ko" if size < 1024 * 1024 else f"{size / 1024 / 1024:.1f} Mo".replace(".", ",")


@bp.app_template_filter("link_host")
def link_host(url):
    host = urlsplit(url).hostname or ""
    try:
        return host.encode("idna").decode("ascii")
    except UnicodeError:
        return host
