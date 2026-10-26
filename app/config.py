import os


class Config:
    MAX_CONTENT_LENGTH = 16 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_TIME_LIMIT = 3600
    WTF_I18N_ENABLED = False
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_HEADERS_ENABLED = True

    @staticmethod
    def from_environment():
        return {
            "SECRET_KEY": os.environ.get("SECRET_KEY", ""),
            "DATABASE": os.environ.get("DATABASE_PATH", ""),
            "SESSION_COOKIE_SECURE": os.environ.get("SESSION_COOKIE_SECURE", "0") == "1",
        }

    @staticmethod
    def validate(config):
        if len(config["SECRET_KEY"]) < 32:
            raise RuntimeError("SECRET_KEY manquante ou trop courte (32 caractères minimum).")
