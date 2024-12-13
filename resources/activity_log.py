from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from flask import current_app
from db import db
from models import ActivityLogModel
from schemas import ActivityLogSchema


blp = Blueprint("ActivityLogs", "activity_logs", description="Operations on activity logs")


@blp.route("/activity-log/<int:log_id>")
class ActivityLog(MethodView):
    @jwt_required()
    @blp.response(200, ActivityLogSchema)
    def get(self, log_id):
        """Get a specific activity log by ID"""
        logger = current_app.logger
        logger.info(f"Fetching activity log with ID: {log_id}")
        log = ActivityLogModel.query.get_or_404(log_id)
        logger.debug(f"Activity log found: {log}")
        return log

    @jwt_required()
    def delete(self, log_id):
        """Delete a specific activity log by ID"""
        logger = current_app.logger
        logger.info(f"Attempting to delete activity log with ID: {log_id}")
        log = ActivityLogModel.query.get_or_404(log_id)
        try:
            db.session.delete(log)
            db.session.commit()
            logger.info(f"Successfully deleted activity log with ID: {log_id}")
            return {"message": "Activity log deleted."}
        except SQLAlchemyError as err:
            logger.error(f"Error deleting activity log with ID {log_id}: {err}")
            abort(500, message="An error occurred while deleting the activity log.")

    @blp.arguments(ActivityLogSchema)
    @blp.response(200, ActivityLogSchema)
    def put(self, log_data, log_id):
        """Update an existing activity log"""
        logger = current_app.logger
        logger.info(f"Updating activity log with ID: {log_id}")
        log = ActivityLogModel.query.get(log_id)

        if not log:
            logger.warning(f"Activity log with ID {log_id} not found.")
            abort(404, message="Activity log not found.")

        # Update log fields based on the provided data
        log.ticket_id = log_data.get("ticket_id", log.ticket_id)
        log.user_id = log_data.get("user_id", log.user_id)
        log.action = log_data.get("action", log.action)

        try:
            db.session.commit()
            logger.info(f"Successfully updated activity log with ID: {log_id}")
        except SQLAlchemyError as err:
            logger.error(f"Error updating activity log with ID {log_id}: {err}")
            abort(500, message="An error occurred while updating the activity log.")

        return log


@blp.route("/activity-log")
class ActivityLogList(MethodView):
    @jwt_required()
    @blp.response(200, ActivityLogSchema(many=True))
    def get(self):
        """Get a list of all activity logs"""
        logger = current_app.logger
        logger.info("Fetching all activity logs.")
        logs = ActivityLogModel.query.all()
        logger.debug(f"Total activity logs fetched: {len(logs)}")
        return logs

    @jwt_required()
    @blp.arguments(ActivityLogSchema)
    @blp.response(201, ActivityLogSchema)
    def post(self, log_data):
        """Create a new activity log"""
        logger = current_app.logger
        logger.info("Creating a new activity log.")
        log = ActivityLogModel(**log_data)
        try:
            db.session.add(log)
            db.session.commit()
            logger.info(f"Successfully created activity log with ID: {log.id}")
        except SQLAlchemyError as err:
            logger.error(f"Error creating activity log: {err}")
            abort(500, message="An error occurred while inserting the activity log.")

        return log


@blp.route("/activity-log/user/<int:user_id>")
class ActivityLogByUser(MethodView):
    @jwt_required()
    @blp.response(200, ActivityLogSchema(many=True))
    def get(self, user_id):
        """Get activity logs by user_id"""
        logger = current_app.logger
        logger.info(f"Fetching activity logs for user ID: {user_id}")
        logs = ActivityLogModel.query.filter_by(user_id=user_id).all()
        if not logs:
            logger.warning(f"No activity logs found for user ID: {user_id}")
            abort(404, message="No activity logs found for this user.")
        return logs


@blp.route("/activity-log/ticket/<int:ticket_id>")
class ActivityLogByTicket(MethodView):
    @jwt_required()
    @blp.response(200, ActivityLogSchema(many=True))
    def get(self, ticket_id):
        """Get activity logs by ticket_id"""
        logger = current_app.logger
        logger.info(f"Fetching activity logs for ticket ID: {ticket_id}")
        logs = ActivityLogModel.query.filter_by(ticket_id=ticket_id).all()
        if not logs:
            logger.warning(f"No activity logs found for ticket ID: {ticket_id}")
            abort(404, message="No activity logs found for this ticket.")
        return logs
