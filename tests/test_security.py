from app.tasks import repository
from tests.conftest import build_app


def test_sql_injection_is_stored_as_text(app, add_task, page):
    payload = "'); DROP TABLE tasks; --"
    add_task(payload)
    with app.app_context():
        assert repository.get_task(1)["title"] == payload
        assert repository.count_tasks()["all"] == 1
    assert page("/?q=' OR 1=1 --").count("task-link") == 0


def test_html_is_escaped(add_task, page):
    add_task("<script>alert(1)</script>", description='<img src=x onerror="alert(1)">')
    html = page()
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<img src=x" not in html


def test_post_without_csrf_token_is_refused(tmp_path):
    client = build_app(tmp_path, WTF_CSRF_ENABLED=True).test_client()
    assert client.post("/tasks", data={"title": "x"}).status_code == 400
    assert client.post("/tasks/1/delete").status_code == 400


def test_post_with_csrf_token_is_accepted(tmp_path):
    client = build_app(tmp_path, WTF_CSRF_ENABLED=True).test_client()
    html = client.get("/").get_data(as_text=True)
    token = html.split('name="csrf_token" value="')[1].split('"')[0]
    assert client.post("/tasks", data={"title": "x", "csrf_token": token}).status_code == 302


def test_write_actions_refuse_get(client, add_task):
    add_task()
    assert client.get("/tasks/1/delete").status_code == 405
    assert client.get("/tasks/1/toggle").status_code == 405


def test_oversized_request_is_refused(client):
    assert client.post("/tasks", data={"title": "x", "description": "x" * 20000}).status_code == 413


def test_write_routes_are_rate_limited(tmp_path):
    client = build_app(tmp_path, RATELIMIT_ENABLED=True).test_client()
    statuses = [client.post("/tasks", data={"title": "x"}).status_code for _ in range(61)]
    assert statuses[:60] == [302] * 60
    assert statuses[60] == 429


def test_error_pages_do_not_leak_details(client):
    html = client.get("/?edit=999").get_data(as_text=True)
    assert "Traceback" not in html
    assert "Cette page ou cette tâche" in html
