# activity_log_api.py
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

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
        log = ActivityLogModel.query.get_or_404(log_id)
        return log

    @jwt_required()
    def delete(self, log_id):
        """Delete a specific activity log by ID"""
        log = ActivityLogModel.query.get_or_404(log_id)
        db.session.delete(log)
        db.session.commit()
        return {"message": "Activity log deleted."}

    @blp.arguments(ActivityLogSchema)
    @blp.response(200, ActivityLogSchema)
    def put(self, log_data, log_id):
        """Update an existing activity log"""
        log = ActivityLogModel.query.get(log_id)

        if not log:
            abort(404, message="Activity log not found.")

        # Update log fields based on the provided data
        log.ticket_id = log_data.get("ticket_id", log.ticket_id)
        log.user_id = log_data.get("user_id", log.user_id)
        log.action = log_data.get("action", log.action)

        db.session.commit()
        return log

@blp.route("/activity-log")
class ActivityLogList(MethodView):
    @jwt_required()
    @blp.response(200, ActivityLogSchema(many=True))
    def get(self):
        """Get a list of all activity logs"""
        return ActivityLogModel.query.all()

    @jwt_required()
    @blp.arguments(ActivityLogSchema)
    @blp.response(201, ActivityLogSchema)
    def post(self, log_data):
        """Create a new activity log"""
        log = ActivityLogModel(**log_data)
        try:
            db.session.add(log)
            db.session.commit()
        except SQLAlchemyError as err:
            abort(500, message="An error occurred while inserting the activity log.")

        return log

@blp.route("/activity-log/user/<int:user_id>")
class ActivityLogByUser(MethodView):
    @jwt_required()
    @blp.response(200, ActivityLogSchema(many=True))
    def get(self, user_id):
        """Get activity logs by user_id"""
        logs = ActivityLogModel.query.filter_by(user_id=user_id).all()
        if not logs:
            abort(404, message="No activity logs found for this user.")
        return logs


@blp.route("/activity-log/ticket/<int:ticket_id>")
class ActivityLogByTicket(MethodView):
    @jwt_required()
    @blp.response(200, ActivityLogSchema(many=True))
    def get(self, ticket_id):
        """Get activity logs by ticket_id"""
        logs = ActivityLogModel.query.filter_by(ticket_id=ticket_id).all()
        if not logs:
            abort(404, message="No activity logs found for this ticket.")
        return logs