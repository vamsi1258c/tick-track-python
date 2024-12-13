from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError

from flask import current_app
from db import db
from models import TicketModel, UserModel
from schemas import TicketSchema, TicketUpdateSchema

blp = Blueprint("Tickets", "tickets", description="Operations on tickets")


@blp.route("/ticket/<int:ticket_id>")
class Ticket(MethodView):
    @jwt_required()
    @blp.response(200, TicketSchema)
    def get(self, ticket_id):
        """Get a specific ticket by ID"""
        logger = current_app.logger
        try:
            ticket = TicketModel.query.get_or_404(ticket_id)
            logger.info(f"Ticket {ticket_id} retrieved successfully.")
            return ticket
        except Exception as e:
            logger.error(f"Error retrieving ticket {ticket_id}: {e}")
            abort(500, message="An error occurred while retrieving the ticket.")

    @jwt_required()
    def delete(self, ticket_id):
        """Delete a specific ticket by ID"""
        logger = current_app.logger
        try:

            ticket = TicketModel.query.get_or_404(ticket_id)
            db.session.delete(ticket)
            db.session.commit()
            logger.info(f"Ticket {ticket_id} deleted successfully.")
            return {"message": "Ticket deleted."}
        except Exception as e:
            logger.error(f"Error deleting ticket {ticket_id}: {e}")
            abort(500, message="An error occurred while deleting the ticket.")

    @blp.arguments(TicketUpdateSchema)
    @blp.response(200, TicketSchema)
    def put(self, ticket_data, ticket_id):
        """Update an existing ticket"""
        logger = current_app.logger
        try:
            ticket = TicketModel.query.get(ticket_id)

            if not ticket:
                logger.warning(f"Ticket {ticket_id} not found.")
                abort(404, message="Ticket not found.")

            # Update ticket fields only if provided in the request
            ticket.title = ticket_data.get("title", ticket.title)
            ticket.description = ticket_data.get("description", ticket.description)
            ticket.status = ticket_data.get("status", ticket.status)
            ticket.priority = ticket_data.get("priority", ticket.priority)
            ticket.category = ticket_data.get("category", ticket.category)
            ticket.subcategory = ticket_data.get("subcategory", ticket.subcategory)
            ticket.assigned_to = ticket_data.get("assigned_to", ticket.assigned_to)
            ticket.approved_by = ticket_data.get("approved_by", ticket.approved_by)

            db.session.commit()
            logger.info(f"Ticket {ticket_id} updated successfully.")
            return ticket
        except Exception as e:
            logger.error(f"Error updating ticket {ticket_id}: {e}")
            abort(500, message="An error occurred while updating the ticket.")


@blp.route("/ticket")
class TicketList(MethodView):
    @jwt_required()
    @blp.response(200, TicketSchema(many=True))
    def get(self):
        """Get a list of all tickets"""
        logger = current_app.logger
        try:
            tickets = TicketModel.query.all()
            logger.info("All tickets retrieved successfully.")
            return tickets
        except Exception as e:
            logger.error(f"Error retrieving tickets: {e}")
            abort(500, message="An error occurred while retrieving tickets.")

    @jwt_required(fresh=True)
    @blp.arguments(TicketSchema)
    @blp.response(201, TicketSchema)
    def post(self, ticket_data):
        """Create a new ticket"""
        logger = current_app.logger
        try:
            ticket = TicketModel(**ticket_data)
            db.session.add(ticket)
            db.session.commit()

            # Fetch creator's and assignee's usernames (which are emails)
            creator = UserModel.query.get(ticket.created_by)
            assignee = UserModel.query.get(ticket.assigned_to) if ticket.assigned_to else None
            approver = UserModel.query.get(ticket.approved_by) if ticket.approved_by else None

            # Prepare recipients list (creator and assignee)
            recipients = [creator.username]
            if assignee:
                recipients.append(assignee.username)
            if approver:
                recipients.append(approver.username)

            logger.info(f"Ticket created successfully with ID {ticket.id}.")
            return ticket
        except SQLAlchemyError as e:
            logger.error(f"Database error while creating ticket: {e}")
            abort(500, message="An error occurred while inserting the ticket.")
        except Exception as e:

            logger.error(f"Unexpected error while creating ticket: {e}")
            abort(500, message="An unexpected error occurred.")
