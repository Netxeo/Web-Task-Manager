from datetime import date, timedelta

from app.tasks.data import tasks as task_data


def column_html(html, status):
    return html.split(f'id="column-{status}"')[1].split("</section>")[0]


def test_columns_group_tasks_by_status(client, add_task, page):
    add_task("A faire", status="new")
    add_task("En route", status="in_progress")
    add_task("Fini", status="done")
    html = page()
    assert "A faire" in column_html(html, "new")
    assert "En route" in column_html(html, "in_progress")
    assert "Fini" in column_html(html, "done")


def test_cards_are_sorted_by_priority(add_task, page):
    add_task("Sans priorité")
    add_task("Basse", priority="1")
    add_task("Haute", priority="3")
    add_task("Moyenne", priority="2")
    column = column_html(page(), "new")
    positions = [column.index(f">{title}</a>") for title in ("Haute", "Moyenne", "Basse", "Sans priorité")]
    assert positions == sorted(positions)


def test_move_endpoint_used_by_drag_and_drop(app, client, add_task):
    add_task("Glissée")
    response = client.post("/tasks/1/status", data={"status": "done"}, headers={"Accept": "application/json"})
    assert response.status_code == 204
    with app.app_context():
        task = task_data.get_task(1)
    assert task["status"] == "done" and task["completed_at"]
    assert client.post("/tasks/1/status", data={"status": "archived"}).status_code == 400


def test_schedule_keeps_time_and_updates_column(app, client, add_task):
    add_task("Rendez-vous", due_at="2030-01-15T14:30", status="in_progress")
    client.post("/tasks/1/schedule", data={"day": "2030-02-01"}, headers={"Accept": "application/json"})
    with app.app_context():
        task = task_data.get_task(1)
    assert (task["due_at"], task["status"]) == ("2030-02-01T14:30", "in_progress")


def test_schedule_new_task_and_unschedule(app, client, add_task):
    add_task("Sans date")
    client.post("/tasks/1/schedule", data={"day": "2030-02-01"})
    with app.app_context():
        assert (task_data.get_task(1)["due_at"], task_data.get_task(1)["status"]) == ("2030-02-01T09:00", "scheduled")
    client.post("/tasks/1/schedule", data={"day": ""})
    with app.app_context():
        assert (task_data.get_task(1)["due_at"], task_data.get_task(1)["status"]) == (None, "new")
    assert client.post("/tasks/1/schedule", data={"day": "demain"}).status_code == 400


def test_planner_shows_week_and_backlog(add_task, page):
    today = date.today()
    add_task("Cette semaine", due_at=f"{today:%Y-%m-%d}T10:00")
    add_task("Plus tard", due_at=f"{today + timedelta(days=30):%Y-%m-%d}T10:00")
    add_task("Sans échéance")
    html = page("/?view=planner")
    assert "Cette semaine" in html and "Sans échéance" in html and "Plus tard" not in html
    assert "Plus tard" in page(f"/?view=planner&week={today + timedelta(days=30)}")


def test_card_shows_counters(client, add_task, page):
    add_task("Avec détails")
    client.post("/tasks/1/subtasks", data={"title": "Étape"})
    client.post("/tasks/1/comments", data={"body": "Note"})
    html = column_html(page(), "new")
    assert "0/1" in html and "commentaires" in html
