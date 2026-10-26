from datetime import date, datetime, timedelta

import pytest

from app.tasks import repository
from app.tasks.moments import done_group, due_group, group_tasks


def at(days, hour=10):
    moment = datetime.combine(date.today() + timedelta(days=days), datetime.min.time()).replace(hour=hour)
    return f"{moment:%Y-%m-%dT%H:%M}"


@pytest.fixture
def planned(add_task):
    add_task("Retard", due_at=at(-2))
    add_task("Ce matin", due_at=at(0, 8))
    add_task("Demain", due_at=at(1))
    add_task("Dans 5 jours", due_at=at(5))
    add_task("Dans un mois", due_at=at(30))
    add_task("Un jour")


def test_today_view_shows_overdue_and_today(planned, page):
    html = page("/?view=today")
    assert "Retard" in html and "Ce matin" in html
    assert "Demain" not in html.split("task-list")[-1]
    assert html.index("En retard") < html.index("Ce matin")


def test_upcoming_view_covers_next_seven_days(planned, page):
    html = page("/?view=upcoming")
    assert "Dans 5 jours" in html
    assert "Dans un mois" not in html
    assert "Ce matin" not in html


def test_todo_view_groups_by_moment(planned, page):
    html = page("/")
    headings = ["En retard", "Aujourd&#39;hui", "Demain", "Dans les 7 jours", "Plus tard", "Sans échéance"]
    positions = [html.index(f'class="group-heading" id="group-{key}">{label}') for key, label in zip(
        ["overdue", "today", "tomorrow", "week", "later", "someday"], headings
    )]
    assert positions == sorted(positions)


def test_completion_is_dated_and_counted(app, client, planned, page):
    client.post("/tasks/2/toggle")
    with app.app_context():
        task = repository.get_task(2)
        counts = repository.count_tasks()
    assert task["completed_at"][:10] == date.today().isoformat()
    assert counts["done_today"] == 1
    assert counts["today"] == 1
    assert "1 sur 2 faites aujourd'hui" in page("/")
    client.post("/tasks/2/toggle")
    with app.app_context():
        assert repository.get_task(2)["completed_at"] is None


def test_sidebar_counts(planned, page):
    html = page("/")
    assert 'view-today' in html
    with_counts = html.split('aria-label="Vues"')[1].split("</nav>")[0]
    assert [part.split("</span>")[0] for part in with_counts.split('class="count">')[1:]] == ["2", "2", "6", "0"]


def test_empty_today_celebrates_when_everything_is_done(client, add_task, page):
    add_task("Seule tâche", due_at=at(0))
    client.post("/tasks/1/toggle")
    assert "Tout est fait pour aujourd&#39;hui." in page("/?view=today")


def test_quick_add_from_today_explains_where_the_task_went(client):
    response = client.post("/tasks", data={"title": "Sans date", "filter_view": "today"}, follow_redirects=True)
    assert "Tâche ajoutée dans « À faire »" in response.get_data(as_text=True)


def test_group_helpers():
    assert due_group(None) == "someday"
    assert due_group(at(-1)) == "overdue"
    assert due_group(at(8)) == "later"
    assert done_group(f"{datetime.now():%Y-%m-%dT%H:%M:%S}") == "today"
    tasks = [{"due_at": at(1)}, {"due_at": None}]
    assert [key for key, _, _ in group_tasks(tasks, "todo")] == ["tomorrow", "someday"]
