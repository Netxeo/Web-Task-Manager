import pytest


@pytest.fixture
def seeded(add_task):
    add_task("Écrire le rapport", description="Chapitre budget", priority="3", tags="travail")
    add_task("Arroser les plantes", priority="1", tags="maison")
    add_task("Payer 100% de la facture", tags="admin")


def titles(html):
    return [title for title in ("Écrire le rapport", "Arroser les plantes", "Payer 100% de la facture") if title in html]


def test_search_matches_title_and_description(seeded, page):
    assert titles(page("/?q=rapport")) == ["Écrire le rapport"]
    assert titles(page("/?q=budget")) == ["Écrire le rapport"]


def test_search_treats_wildcards_literally(seeded, page):
    assert titles(page("/?q=100%25")) == ["Payer 100% de la facture"]
    assert titles(page("/?q=_")) == []


def test_tag_and_priority_filters(seeded, page):
    assert titles(page("/?tag=maison")) == ["Arroser les plantes"]
    assert titles(page("/?priority=3")) == ["Écrire le rapport"]


def test_filters_also_apply_to_planner(seeded, page):
    assert titles(page("/?view=planner&tag=admin")) == ["Payer 100% de la facture"]


def test_invalid_parameters_fall_back_to_defaults(seeded, client):
    response = client.get("/?view=hack&priority=7&tag=<b>&week=2026-99-99")
    assert response.status_code == 200
    assert len(titles(response.get_data(as_text=True))) == 3


def test_empty_result_offers_to_clear_filters(seeded, page):
    html = page("/?q=introuvable")
    assert "Aucune tâche ne correspond" in html
    assert "Effacer les filtres" in html
