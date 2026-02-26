import os


class Config:
    """Flask application configuration."""

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'decisions.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")


class TestConfig(Config):
    """Configuration for testing — uses in-memory SQLite."""

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
