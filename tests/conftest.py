import pytest

from app import create_app

TEST_SECRET = "test-secret-key-for-automated-tests-only"


def build_app(tmp_path, **overrides):
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": TEST_SECRET,
            "DATABASE": str(tmp_path / "test.db"),
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
            "WTF_CSRF_ENABLED": False,
            "RATELIMIT_ENABLED": False,
            **overrides,
        }
    )


@pytest.fixture
def app(tmp_path):
    return build_app(tmp_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def add_task(client):
    def add(title="Tâche", **fields):
        return client.post("/tasks", data={"title": title, **fields})

    return add


@pytest.fixture
def page(client):
    def get(url="/"):
        return client.get(url).get_data(as_text=True)

    return get
