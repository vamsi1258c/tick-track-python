import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate


from db import db
from blocklist import BLOCKLIST

from resources.user import blp as UserBlueprint
from resources.ticket import blp as TicketBluprint
from resources.attachment import blp as AttachmentBluprint
from resources.comment import blp as CommentBluprint
from resources.activity_log import blp as ActivityLogBluprint


def create_app(db_url=None):
    app = Flask(__name__)

    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    db_url = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "postgresql://postgres:vamsi@localhost:5432/admin"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    db.init_app(app)
    migrate = Migrate(app, db)

    api = Api(app)

    app.config["JWT_SECRET_KEY"] = "vamsi"
    jwt = JWTManager(app)

    CORS(app, supports_credentials=True)


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

    api.register_blueprint(UserBlueprint)
    api.register_blueprint(TicketBluprint)
    api.register_blueprint(AttachmentBluprint)
    api.register_blueprint(CommentBluprint)
    api.register_blueprint(ActivityLogBluprint)


    return app
