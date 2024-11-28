from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError

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
        ticket = TicketModel.query.get_or_404(ticket_id)
        return ticket

    @jwt_required()
    def delete(self, ticket_id):
        """Delete a specific ticket by ID"""
        # jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privilege required.")

        ticket = TicketModel.query.get_or_404(ticket_id)
        db.session.delete(ticket)
        db.session.commit()
        return {"message": "Ticket deleted."}

    @blp.arguments(TicketUpdateSchema)
    @blp.response(200, TicketSchema)
    def put(self, ticket_data, ticket_id):
        """Update an existing ticket"""
        ticket = TicketModel.query.get(ticket_id)

        if not ticket:
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

        print(ticket_data)

        db.session.commit()
        return ticket

@blp.route("/ticket")
class TicketList(MethodView):
    @jwt_required()
    @blp.response(200, TicketSchema(many=True))
    def get(self):
        """Get a list of all tickets"""
        return TicketModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(TicketSchema)
    @blp.response(201, TicketSchema)
    def post(self, ticket_data):
        """Create a new ticket"""
        ticket = TicketModel(**ticket_data)
        try:
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

        except SQLAlchemyError as err:
            abort(500, message="An error occurred while inserting the ticket.")


        return ticket
