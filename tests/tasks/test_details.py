import pytest

from app.tasks.data import details


@pytest.fixture
def task(add_task):
    add_task("Tâche principale")
    add_task("Autre tâche")
    return 1


def test_subtasks_add_toggle_delete(app, client, task):
    response = client.post("/tasks/1/subtasks", data={"title": "Étape 1"})
    assert response.headers["Location"] == "/?edit=1&tab=subtasks"
    client.post("/tasks/1/subtasks/1/toggle")
    with app.app_context():
        assert [tuple(row) for row in details.list_subtasks(1)] == [(1, "Étape 1", 1)]
    client.post("/tasks/1/subtasks/1/delete")
    with app.app_context():
        assert details.list_subtasks(1) == []


def test_details_cannot_be_reached_through_another_task(client, task):
    client.post("/tasks/1/subtasks", data={"title": "Étape"})
    client.post("/tasks/1/comments", data={"body": "Note"})
    assert client.post("/tasks/2/subtasks/1/toggle").status_code == 404
    assert client.post("/tasks/2/subtasks/1/delete").status_code == 404
    assert client.post("/tasks/2/comments/1/delete").status_code == 404


def test_subtask_limit(app, client, task):
    for number in range(21):
        client.post("/tasks/1/subtasks", data={"title": f"Étape {number}"})
    with app.app_context():
        assert len(details.list_subtasks(1)) == details.LIMITS["subtasks"]


def test_comments_are_escaped_and_kept_with_line_breaks(client, task, page):
    client.post("/tasks/1/comments", data={"body": "Ligne 1\nLigne 2 <img src=x onerror=alert(1)>"})
    html = page("/?edit=1&tab=comments")
    assert "<img src=x" not in html
    assert "Ligne 1\nLigne 2 &lt;img" in html


def test_empty_comment_is_refused(client, task):
    response = client.post("/tasks/1/comments", data={"body": "   "})
    assert response.status_code == 422
    assert "Le commentaire est vide." in response.get_data(as_text=True)


@pytest.mark.parametrize(
    "url",
    ["javascript:alert(1)", "data:text/html,<b>x</b>", "ftp://example.com", "https://user:pass@example.com", "https://", "https://exa mple.com"],
)
def test_dangerous_links_are_refused(app, client, task, url):
    assert client.post("/tasks/1/links", data={"url": url}).status_code == 422
    with app.app_context():
        assert details.list_links(1) == []


def test_valid_link_opens_safely(client, task, page):
    client.post("/tasks/1/links", data={"url": "https://example.com/doc?a=1", "label": "Documentation"})
    html = page("/?edit=1&tab=resources")
    assert 'href="https://example.com/doc?a=1" target="_blank" rel="noopener noreferrer nofollow"' in html
    assert "Documentation" in html


def test_link_shows_its_real_domain(client, task, page):
    client.post("/tasks/1/links", data={"url": "https://\u0430pple.com/login", "label": "apple.com"})
    assert "xn--pple-43d.com" in page("/?edit=1&tab=resources")
