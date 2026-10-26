import os


class Config:
    MAX_CONTENT_LENGTH = 6 * 1024 * 1024
    MAX_FORM_MEMORY_SIZE = 16 * 1024
    MAX_FORM_PARTS = 50
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"
    WTF_CSRF_TIME_LIMIT = 3600
    WTF_I18N_ENABLED = False
    UPLOAD_FOLDER = ""
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
