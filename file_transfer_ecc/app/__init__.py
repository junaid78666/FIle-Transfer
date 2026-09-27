"""
app/__init__.py — Application Factory
======================================
Creates and configures the Flask application.

Usage:
    from app import create_app
    app = create_app()               # → DevelopmentConfig
    app = create_app("testing")      # → TestingConfig
    app = create_app("production")   # → ProductionConfig
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

from app.config import config_map

# ── Extension instances (uninitialised) ───────────────────────
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()
migrate = Migrate()


def create_app(config_name: str = None) -> Flask:
    """
    Flask application factory.

    Args:
        config_name: One of "development", "testing", "production".
                     Defaults to FLASK_ENV env-var or "development".

    Returns:
        Configured Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, instance_relative_config=True)

    # ── Load configuration ────────────────────────────────────
    app.config.from_object(config_map.get(config_name, config_map["default"]))

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    # Ensure uploads folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ── Initialise extensions ─────────────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # ── Configure Flask-Login ─────────────────────────────────
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"           # Redirect here if not authenticated
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    login_manager.session_protection = "strong"

    # ── User loader callback ──────────────────────────────────
    from app.models.user import User  # Import here to avoid circular imports

    @login_manager.user_loader
    def load_user(user_id: str):
        """Load user by ID for Flask-Login session management."""
        return User.query.get(int(user_id))

    # ── Register Blueprints ───────────────────────────────────
    _register_blueprints(app)

    # ── Register error handlers ───────────────────────────────
    _register_error_handlers(app)

    # ── Shell context (flask shell) ───────────────────────────
    @app.shell_context_processor
    def make_shell_context():
        from app.models.user import User
        from app.models.ecc_key import ECCKey
        from app.models.transfer import Transfer
        return {"db": db, "User": User, "ECCKey": ECCKey, "Transfer": Transfer}

    return app


def _register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    from app.auth.routes import auth_bp
    from app.transfer.routes import transfer_bp
    from app.main.routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(transfer_bp, url_prefix="/transfer")


def _register_error_handlers(app: Flask) -> None:
    """Register custom HTTP error handlers."""
    from flask import jsonify, render_template

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"status": "error", "message": "Bad request.", "code": 400}), 400

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"status": "error", "message": "Access forbidden.", "code": 403}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"status": "error", "message": "Resource not found.", "code": 404}), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return jsonify({
            "status": "error",
            "message": "File is too large. Maximum allowed size exceeded.",
            "code": 413,
        }), 413

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()  # Rollback on server error
        return jsonify({"status": "error", "message": "Internal server error.", "code": 500}), 500
