import os
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from db import db
from models import ConfigMasterModel
from schemas import ConfigMasterSchema, ConfigMasterUpdateSchema

blp = Blueprint("ConfigMaster", "configMaster", description="Operations on configuration settings")

@blp.route("/configmaster/<int:config_id>")
class ConfigMaster(MethodView):
    @jwt_required()
    @blp.response(200, ConfigMasterSchema)
    def get(self, config_id):
        """Get a specific configuration by ID"""
        config = ConfigMasterModel.query.get_or_404(config_id)
        return config

    @jwt_required()
    def delete(self, config_id):
        """Delete a specific configuration by ID"""
        config = ConfigMasterModel.query.get_or_404(config_id)
        db.session.delete(config)
        db.session.commit()
        return {"message": "Configuration deleted."}

    @blp.arguments(ConfigMasterUpdateSchema)
    @blp.response(200, ConfigMasterSchema)
    def put(self, config_data, config_id):
        """Update an existing configuration"""
        config = ConfigMasterModel.query.get(config_id)

        if not config:
            abort(404, message="Configuration not found.")

        # Update configuration fields only if provided in the request
        config.type = config_data.get("type", config.type)
        config.value = config_data.get("value", config.value)
        config.label = config_data.get("label", config.label)
        config.color = config_data.get("color", config.color)
        config.parent = config_data.get("parent", config.parent)

        db.session.commit()
        return config

@blp.route("/configmaster")
class ConfigMasterList(MethodView):
    @jwt_required()
    @blp.response(200, ConfigMasterSchema(many=True))
    def get(self):
        """Get a list of all configurations"""
        return ConfigMasterModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(ConfigMasterSchema)
    @blp.response(201, ConfigMasterSchema)
    def post(self, config_data):
        """Create a new configuration"""
        config = ConfigMasterModel(**config_data)
        try:
            db.session.add(config)
            db.session.commit()

            # Optional: Send an email notification after creating the configuration
            # send_email(
            #     sender_email=os.getenv("SENDER_EMAIL"),  # Set your sender email
            #     to_email=["admin@example.com"],  # List of recipients
            #     subject="New Configuration Created",
            #     message_text=f"A new configuration has been created: {config.label} ({config.value})"
            # )
        except SQLAlchemyError as err:
            abort(500, message="An error occurred while inserting the configuration.")

        return config
