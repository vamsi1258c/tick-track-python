from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app

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
        logger = current_app.logger
        logger.info(f"Retrieving configuration with ID {config_id}.")
        config = ConfigMasterModel.query.get_or_404(config_id)
        logger.info(f"Successfully retrieved configuration with ID {config_id}.")
        return config

    @jwt_required()
    def delete(self, config_id):
        """Delete a specific configuration by ID"""
        logger = current_app.logger
        logger.info(f"Deleting configuration with ID {config_id}.")
        config = ConfigMasterModel.query.get_or_404(config_id)
        db.session.delete(config)
        db.session.commit()
        logger.info(f"Successfully deleted configuration with ID {config_id}.")
        return {"message": "Configuration deleted."}

    @blp.arguments(ConfigMasterUpdateSchema)
    @blp.response(200, ConfigMasterSchema)
    def put(self, config_data, config_id):
        """Update an existing configuration"""
        logger = current_app.logger
        logger.info(f"Updating configuration with ID {config_id}.")
        config = ConfigMasterModel.query.get(config_id)

        if not config:
            logger.warning(f"Configuration with ID {config_id} not found.")
            abort(404, message="Configuration not found.")

        # Update configuration fields only if provided in the request
        config.type = config_data.get("type", config.type)
        config.value = config_data.get("value", config.value)
        config.label = config_data.get("label", config.label)
        config.color = config_data.get("color", config.color)
        config.parent = config_data.get("parent", config.parent)

        try:
            db.session.commit()
            logger.info(f"Successfully updated configuration with ID {config_id}.")
        except SQLAlchemyError as e:
            logger.error(f"Error while updating configuration with ID {config_id}: {e}")
            abort(500, message="An error occurred while updating the configuration.")

        return config


@blp.route("/configmaster")
class ConfigMasterList(MethodView):
    @jwt_required()
    @blp.response(200, ConfigMasterSchema(many=True))
    def get(self):
        """Get a list of all configurations"""
        logger = current_app.logger
        logger.info("Retrieving all configurations.")
        configs = ConfigMasterModel.query.all()
        logger.info(f"Successfully retrieved {len(configs)} configurations.")
        return configs

    @jwt_required(fresh=True)
    @blp.arguments(ConfigMasterSchema)
    @blp.response(201, ConfigMasterSchema)
    def post(self, config_data):
        """Create a new configuration"""
        logger = current_app.logger
        logger.info(f"Creating new configuration with data: {config_data}")
        config = ConfigMasterModel(**config_data)
        try:
            db.session.add(config)
            db.session.commit()
            logger.info(f"Successfully created new configuration: {config.label} ({config.value})")

        except SQLAlchemyError as err:
            logger.error(f"Error while inserting new configuration: {err}")
            abort(500, message="An error occurred while inserting the configuration.")

        return config
