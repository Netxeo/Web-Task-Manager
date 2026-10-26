import pytest

from app.tasks import repository


@pytest.mark.parametrize(
    "fields, message",
    [
        ({"title": ""}, "Le titre est obligatoire."),
        ({"title": "   "}, "Le titre est obligatoire."),
        ({"title": "x" * 121}, "120 caractères maximum."),
        ({"title": "ok", "description": "x" * 2001}, "2000 caractères maximum."),
        ({"title": "ok", "priority": "9"}, "pas un choix valide"),
        ({"title": "ok", "due_at": "demain"}, "pas une date/heure valide"),
        ({"title": "ok", "tags": "<script>"}, "Tag invalide"),
        ({"title": "ok", "tags": "a, b, c, d, e, f"}, "5 tags maximum par tâche."),
        ({"title": "ok", "tags": "x" * 25}, "Tag invalide"),
    ],
)
def test_invalid_input_is_rejected(app, client, fields, message):
    response = client.post("/tasks", data=fields)
    assert response.status_code == 422
    assert message in response.get_data(as_text=True)
    with app.app_context():
        assert repository.count_tasks()["all"] == 0


def test_control_characters_are_stripped(app, add_task):
    add_task("Ti\x00tre\x07 propre")
    with app.app_context():
        assert repository.get_task(1)["title"] == "Titre propre"


def test_duplicate_tags_are_merged(app, add_task):
    add_task(tags="Admin, admin,  ADMIN ")
    with app.app_context():
        assert repository.get_task(1)["tags"] == ["admin"]
