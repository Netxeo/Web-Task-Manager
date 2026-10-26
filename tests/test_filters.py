import pytest


@pytest.fixture
def seeded(client, add_task):
    add_task("Écrire le rapport", description="Chapitre budget", priority="3", tags="travail", due_at="2030-03-01T10:00")
    add_task("Arroser les plantes", priority="1", tags="maison", due_at="2030-01-01T08:00")
    add_task("Payer 100% de la facture", tags="admin")
    add_task("Lire un livre")
    client.post("/tasks/4/toggle")


def titles(html):
    return [title for title in ("Écrire le rapport", "Arroser les plantes", "Payer 100% de la facture", "Lire un livre") if title in html]


def test_status_filter(seeded, page):
    assert titles(page("/?status=done")) == ["Lire un livre"]
    assert "Lire un livre" not in page("/?status=todo")


def test_search_matches_title_and_description(seeded, page):
    assert titles(page("/?q=rapport")) == ["Écrire le rapport"]
    assert titles(page("/?q=budget")) == ["Écrire le rapport"]


def test_search_treats_wildcards_literally(seeded, page):
    assert titles(page("/?q=100%25")) == ["Payer 100% de la facture"]
    assert titles(page("/?q=%25")) == ["Payer 100% de la facture"]
    assert titles(page("/?q=_")) == []


def test_tag_and_priority_filters(seeded, page):
    assert titles(page("/?tag=maison")) == ["Arroser les plantes"]
    assert titles(page("/?priority=3")) == ["Écrire le rapport"]


def test_sort_by_due_date_puts_undated_last(seeded, page):
    html = page("/?sort=due&status=todo")
    assert html.index("Arroser les plantes") < html.index("Écrire le rapport") < html.index("Payer 100%")


def test_sort_by_priority(seeded, page):
    html = page("/?sort=priority&status=todo")
    assert html.index("Écrire le rapport") < html.index("Arroser les plantes") < html.index("Payer 100%")


def test_invalid_parameters_fall_back_to_defaults(seeded, client):
    response = client.get("/?status=hack&sort=id;DROP&priority=7&tag=<b>")
    assert response.status_code == 200
    assert len(titles(response.get_data(as_text=True))) == 4


def test_empty_search_shows_reset_link(seeded, page):
    html = page("/?q=introuvable")
    assert "Aucune tâche ne correspond" in html
    assert "Effacer les filtres" in html
