import io

from app.tasks.data import tasks as task_data
from tests.conftest import build_app


def test_sql_injection_is_stored_as_text(app, add_task, page):
    payload = "'); DROP TABLE tasks; --"
    add_task(payload)
    with app.app_context():
        assert task_data.get_task(1)["title"] == payload
        assert task_data.count_tasks() == 1
    assert page("/?q=' OR 1=1 --").count("card-link") == 0


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


def test_out_of_range_identifiers_return_404(client):
    huge = "9" * 30
    assert client.get(f"/?edit={huge}").status_code == 200
    assert client.get("/?edit=0").status_code == 200
    for path in (f"/tasks/{huge}", f"/tasks/{huge}/toggle", f"/tasks/{huge}/status", "/tasks/0/delete"):
        assert client.post(path, data={"title": "x", "status": "done"}).status_code == 404
    assert client.get(f"/tasks/1/attachments/{huge}").status_code == 404


def test_chunked_body_is_cut_at_the_size_limit(client):
    response = client.post(
        "/tasks",
        input_stream=io.BytesIO(b"title=" + b"x" * 30000),
        headers={"Content-Type": "application/x-www-form-urlencoded", "Transfer-Encoding": "chunked"},
        environ_overrides={"wsgi.input_terminated": True},
    )
    assert response.status_code in (413, 422)


def test_extreme_planner_weeks_do_not_crash(client):
    for week in ("9999-12-31", "0001-01-01", "2026-02-30", "x" * 50):
        assert client.get(f"/?view=planner&week={week}").status_code == 200


def test_writes_from_other_sites_are_blocked(client, add_task):
    for origin in ("cross-site", "same-site"):
        assert client.post("/tasks", data={"title": "Piège"}, headers={"Sec-Fetch-Site": origin}).status_code == 403
    assert client.post("/tasks", data={"title": "Normal"}, headers={"Sec-Fetch-Site": "same-origin"}).status_code == 302


def test_hidden_unicode_characters_are_removed(app, add_task):
    add_task("Payer\u202e009 \u200bfacture", tags="Cafe\u0301, \uff21\uff24\uff2d\uff29\uff2e")
    with app.app_context():
        task = task_data.get_task(1)
    assert task["title"] == "Payer009 facture"
    assert task["tags"] == ["admin", "café"]


def test_session_cookie_is_strict(client):
    client.post("/tasks", data={"title": ""})
    response = client.post("/tasks", data={"title": "Ok"})
    cookie = response.headers.get("Set-Cookie", "")
    assert "HttpOnly" in cookie and "SameSite=Strict" in cookie
