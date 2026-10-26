# Web Task Manager

Application web de gestion de tâches en Python : créer, modifier, supprimer et marquer des tâches comme terminées.

> Projet en cours de développement. Le suivi détaillé est dans [DEVLOG.md](DEVLOG.md).

## Stack

| Couche | Choix |
|---|---|
| Langage | Python 3.12+ |
| Framework | Flask 3 |
| Base de données | SQLite (module `sqlite3` de Python, sans ORM) |
| Interface | HTML rendu par le serveur (Jinja2), CSS et JavaScript natifs |
| Sécurité | Flask-WTF (CSRF), Flask-Limiter (limitation de débit), en-têtes HTTP stricts |
| Tests | pytest, pip-audit |

## Installation

Prérequis : Python 3.12 ou plus récent.

```bash
git clone https://github.com/Netxeo/Web-Task-Manager.git
cd Web-Task-Manager
python -m venv .venv
```

Activer l'environnement sous Windows :

```bash
.venv\Scripts\activate
```

Sous macOS ou Linux :

```bash
source .venv/bin/activate
```

Installer les dépendances et créer le fichier de configuration :

```bash
pip install -r requirements.txt
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Coller la valeur générée après `SECRET_KEY=` dans `.env`, puis lancer l'application :

```bash
flask --app app run
```

L'application est disponible sur http://127.0.0.1:5000. La base SQLite est créée automatiquement dans `instance/tasks.db`.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
pip-audit -r requirements.txt
```

## Architecture

```
app/
├── __init__.py      création de l'application
├── config.py        configuration lue depuis l'environnement
├── extensions.py    CSRF et limitation de débit
├── security.py      en-têtes HTTP de sécurité
├── errors.py        pages d'erreur
├── db.py            connexion SQLite
├── schema.sql       schéma de la base
├── tasks/           module des tâches (routes, accès aux données)
├── templates/       vues Jinja2
└── static/          CSS et JavaScript
tests/               tests automatisés
```

Organisation MVC : `tasks/repository.py` porte les requêtes SQL (modèle), `templates/` l'affichage (vue), `tasks/routes.py` les routes HTTP (contrôleur).

## Pourquoi SQLite

- Gratuit, sans compte, sans quota, inclus dans Python.
- Aucun serveur ni port réseau ouvert, aucun identifiant de base à protéger.
- Transactions ACID et table en mode `STRICT` avec contraintes `CHECK` : la base refuse elle-même les données invalides.
- Limite assumée : une seule écriture à la fois, parfait pour un usage individuel. L'accès aux données est isolé dans un seul module pour pouvoir passer à PostgreSQL si besoin.

## Typographie

Atkinson Hyperlegible Next et Atkinson Hyperlegible Mono (Braille Institute), choisies pour leur lisibilité : chaque caractère facile à confondre (I, l, 1, O, 0) a une forme distincte. Fichiers hébergés dans `app/static/fonts`, sous licence SIL Open Font License 1.1.

## Licence

Code source disponible sous [PolyForm Noncommercial 1.0.0](LICENSE).

- Consultation, étude et modification autorisées à des fins non commerciales.
- Toute utilisation commerciale est interdite.
- Le crédit de l'auteur est obligatoire : la ligne `Required Notice` du fichier `LICENSE` doit être conservée dans toute copie ou redistribution.

© 2026 Paul Noorman, [Netxeo](https://github.com/Netxeo)
