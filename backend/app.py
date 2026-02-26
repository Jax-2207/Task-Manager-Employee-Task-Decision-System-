"""Flask application factory and entry point."""

import logging

from flask import Flask, jsonify
from flask_cors import CORS
from marshmallow import ValidationError as MarshmallowValidationError

from config import Config
from exceptions import (
    InvalidStateTransitionError,
    NotFoundError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
)
from models import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Register blueprints
    from routes.decision_routes import decisions_bp
    from routes.auth_routes import auth_bp
    from routes.whatsapp_routes import whatsapp_bp

    app.register_blueprint(decisions_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(whatsapp_bp)

    # --- Global error handlers ---

    @app.errorhandler(NotFoundError)
    def handle_not_found(error):
        return jsonify({"error": error.message}), 404

    @app.errorhandler(InvalidStateTransitionError)
    def handle_invalid_transition(error):
        return jsonify({"error": error.message}), 400

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({"error": error.message}), 400

    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_error(error):
        return jsonify({"error": error.messages}), 400

    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized(error):
        return jsonify({"error": error.message}), 401

    @app.errorhandler(ForbiddenError)
    def handle_forbidden(error):
        return jsonify({"error": error.message}), 403

    @app.errorhandler(404)
    def handle_generic_404(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def handle_500(error):
        logger.error("Internal server error: %s", error)
        return jsonify({"error": "Internal server error"}), 500

    # Create tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)

