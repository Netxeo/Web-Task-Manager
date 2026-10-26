from app.tasks.data import tasks as task_data


def test_create_task_with_all_fields(app, add_task, page):
    response = add_task(
        "Préparer la démo", description="Script de 5 minutes", status="in_progress",
        priority="3", due_at="2030-01-15T09:30", tags="Travail, démo",
    )
    assert response.status_code == 302
    with app.app_context():
        task = task_data.get_task(1)
    assert (task["status"], task["priority"], task["due_at"]) == ("in_progress", 3, "2030-01-15T09:30")
    assert task["tags"] == ["démo", "travail"]
    assert "Préparer la démo" in page()


def test_quick_add_lands_in_new_column(app, add_task):
    add_task("Acheter du pain")
    with app.app_context():
        task = task_data.get_task(1)
    assert (task["status"], task["priority"], task["due_at"], task["tags"]) == ("new", 0, None, [])


def test_new_task_with_date_is_scheduled(app, add_task):
    add_task("Rendez-vous", due_at="2030-01-15T09:30")
    with app.app_context():
        assert task_data.get_task(1)["status"] == "scheduled"


def test_update_task(app, client, add_task):
    add_task("Ancien titre", tags="a, b")
    response = client.post("/tasks/1", data={"title": "Nouveau titre", "status": "in_progress", "priority": "2", "tags": "b, c"})
    assert response.status_code == 302
    with app.app_context():
        task = task_data.get_task(1)
        tags = [row["name"] for row in task_data.list_tags()]
    assert (task["title"], task["status"], task["priority"], task["tags"]) == ("Nouveau titre", "in_progress", 2, ["b", "c"])
    assert tags == ["b", "c"]


def test_toggle_completes_and_reopens(app, client, add_task):
    add_task("Avec date", due_at="2030-01-15T09:30")
    client.post("/tasks/1/toggle")
    with app.app_context():
        task = task_data.get_task(1)
    assert task["status"] == "done" and task["completed_at"]
    client.post("/tasks/1/toggle")
    with app.app_context():
        task = task_data.get_task(1)
    assert task["status"] == "scheduled" and task["completed_at"] is None


def test_delete_task_removes_orphan_tags(app, client, add_task):
    add_task(tags="unique")
    assert client.post("/tasks/1/delete").status_code == 302
    with app.app_context():
        assert task_data.get_task(1) is None
        assert task_data.list_tags() == []


def test_unknown_task_returns_404(client):
    assert client.get("/?edit=999").status_code == 404
    assert client.post("/tasks/999", data={"title": "x"}).status_code == 404
    for action in ("toggle", "delete"):
        assert client.post(f"/tasks/999/{action}").status_code == 404
    assert client.post("/tasks/999/status", data={"status": "done"}).status_code == 404
    assert client.post("/tasks/999/schedule", data={"day": "2030-01-01"}).status_code == 404


def test_edit_panel_is_prefilled_with_tabs(add_task, page):
    add_task("Relire le contrat", description="Article 11", tags="admin")
    html = page("/?edit=1")
    assert 'value="Relire le contrat"' in html and "Article 11</textarea>" in html and 'value="admin"' in html
    for label in ("Détails", "Sous-tâches", "Commentaires", "Fichiers et liens"):
        assert label in html


def test_redirect_keeps_current_filters(add_task):
    response = add_task("Filtrée", priority="3", filter_view="planner", filter_tag="admin", next="https://evil.example")
    assert response.headers["Location"] == "/?view=planner&tag=admin"
