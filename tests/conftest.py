import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key-for-automated-tests-only",
            "DATABASE": str(tmp_path / "test.db"),
        }
    )


@pytest.fixture
def client(app):
    return app.test_client()
