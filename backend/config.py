import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Flask application configuration."""

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Neon/Render provide postgres:// but SQLAlchemy 1.4+ requires postgresql://
    _db_url = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'decisions.db')}"
    )
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")


class TestConfig(Config):
    """Configuration for testing — uses in-memory SQLite."""

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
