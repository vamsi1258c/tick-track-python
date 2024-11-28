import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_mail import Mail, Message

from db import db
from blocklist import BLOCKLIST

# Importing resources
from resources.user import blp as user_blueprint
from resources.ticket import blp as ticket_blueprint
from resources.attachment import blp as attachment_blueprint
from resources.comment import blp as comment_blueprint
from resources.activity_log import blp as activity_log_blueprint
from resources.config_master import blp as config_master_blueprint
from resources.email import blp as email_blueprint

# Initialize extensions
mail = Mail()

def create_app(db_url=None):
    """Factory function to create the Flask app."""
    app = Flask(__name__)

    # API Configurations
    app.config["API_TITLE"] = "TickTrack REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # Database Configurations
    db_url = db_url or os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "postgresql://postgres:vamsi@localhost:5432/admin"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True

    # Mail Configurations
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "13.60.4.6")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "False").lower() == "true"
    app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL", "False").lower() == "true"
    app.config["MAIL_USERNAME"] = None
    app.config["MAIL_PASSWORD"] = None
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER", "noreply@vforit.com")

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    mail.init_app(app)

    # API and JWT Configurations
    api = Api(app)
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "vamsi")
    jwt = JWTManager(app)
    CORS(app, supports_credentials=True)

    # JWT Callbacks
    configure_jwt_callbacks(jwt)

    # Register Blueprints
    register_blueprints(api)

    # Test Mail Route
    @app.route('/send-test-email')
    def send_test_email():
        """Test endpoint to send an email."""
        try:
            msg = Message(
                subject="Test Email from TickTrack",
                recipients=["recipient@example.com"],  # Replace with actual recipient
                body="This is a test email sent from the TickTrack REST API."
            )
            mail.send(msg)
            return jsonify({"message": "Test email sent successfully!"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app


def configure_jwt_callbacks(jwt):
    """Configures JWT callbacks for handling token issues."""

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )


def register_blueprints(api):
    """Registers all the blueprints to the API."""
    api.register_blueprint(user_blueprint)
    api.register_blueprint(ticket_blueprint)
    api.register_blueprint(attachment_blueprint)
    api.register_blueprint(comment_blueprint)
    api.register_blueprint(activity_log_blueprint)
    api.register_blueprint(config_master_blueprint)
    api.register_blueprint(email_blueprint)
