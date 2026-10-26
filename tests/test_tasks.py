from app.tasks import repository


def test_create_task_with_all_fields(app, add_task, page):
    response = add_task(
        "Préparer la démo",
        description="Script de 5 minutes",
        priority="3",
        due_at="2030-01-15T09:30",
        tags="Travail, démo",
    )
    assert response.status_code == 302
    with app.app_context():
        task = repository.get_task(1)
    assert task["title"] == "Préparer la démo"
    assert task["priority"] == 3
    assert task["due_at"] == "2030-01-15T09:30"
    assert task["tags"] == ["démo", "travail"]
    assert "Préparer la démo" in page()


def test_quick_add_uses_defaults(app, add_task):
    add_task("Acheter du pain")
    with app.app_context():
        task = repository.get_task(1)
    assert task["description"] == ""
    assert task["priority"] == 0
    assert task["due_at"] is None
    assert task["tags"] == []


def test_update_task(app, client, add_task):
    add_task("Ancien titre", tags="a, b")
    response = client.post("/tasks/1", data={"title": "Nouveau titre", "priority": "2", "tags": "b, c"})
    assert response.status_code == 302
    with app.app_context():
        task = repository.get_task(1)
        tags = [row["name"] for row in repository.list_tags()]
    assert task["title"] == "Nouveau titre"
    assert task["priority"] == 2
    assert task["tags"] == ["b", "c"]
    assert tags == ["b", "c"]


def test_toggle_task_twice(app, client, add_task):
    add_task()
    client.post("/tasks/1/toggle")
    with app.app_context():
        assert repository.get_task(1)["is_done"] == 1
    client.post("/tasks/1/toggle")
    with app.app_context():
        assert repository.get_task(1)["is_done"] == 0


def test_delete_task_removes_orphan_tags(app, client, add_task):
    add_task(tags="unique")
    response = client.post("/tasks/1/delete")
    assert response.status_code == 302
    with app.app_context():
        assert repository.get_task(1) is None
        assert repository.list_tags() == []


def test_unknown_task_returns_404(client):
    assert client.get("/?edit=999").status_code == 404
    assert client.post("/tasks/999", data={"title": "x"}).status_code == 404
    assert client.post("/tasks/999/toggle").status_code == 404
    assert client.post("/tasks/999/delete").status_code == 404


def test_edit_panel_is_prefilled(add_task, page):
    add_task("Relire le contrat", description="Article 11", tags="admin")
    html = page("/?edit=1")
    assert "Modifier la tâche" in html
    assert 'value="Relire le contrat"' in html
    assert "Article 11</textarea>" in html
    assert 'value="admin"' in html


def test_redirect_keeps_current_filters(add_task):
    response = add_task("Filtrée", priority="3", filter_status="todo", filter_tag="admin", next="https://evil.example")
    assert response.headers["Location"] == "/?status=todo&tag=admin"
