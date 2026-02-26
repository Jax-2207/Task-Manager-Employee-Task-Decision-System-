"""Models package — exports db instance and all models."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.decision import Decision  # noqa: E402, F401
from models.user import User  # noqa: E402, F401
