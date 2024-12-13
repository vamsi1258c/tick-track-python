from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app

from db import db
from models import CommentModel, TicketModel, UserModel
from schemas import CommentSchema, PlainCommentSchema

blp = Blueprint("Comments", "comments", description="Operations on comments")


@blp.route("/ticket/<int:ticket_id>/comments")
class CommentList(MethodView):
    @jwt_required()
    @blp.response(200, CommentSchema(many=True))
    def get(self, ticket_id):
        """Get all comments for a specific ticket"""
        logger = current_app.logger
        try:
            logger.info(f"Retrieving comments for ticket ID {ticket_id}.")
            ticket = TicketModel.query.get_or_404(ticket_id)
            logger.info(f"Successfully retrieved comments for ticket ID {ticket_id}.")
            return ticket.comments  # Return the list of comments for the ticket
        except SQLAlchemyError as e:
            logger.error(f"Error while retrieving comments for ticket ID {ticket_id}: {e}")
            abort(500, message="An error occurred while retrieving the comments.")

    @jwt_required()
    @blp.arguments(CommentSchema)
    @blp.response(201, CommentSchema)
    def post(self, comment_data, ticket_id):
        """Create a new comment on a specific ticket"""
        logger = current_app.logger
        username = get_jwt_identity()  # Get the username from the JWT token
        try:
            ticket = TicketModel.query.get_or_404(ticket_id)  # Fetch the ticket
        except SQLAlchemyError as e:
            logger.error(f"Error while retrieving ticket ID {ticket_id}: {e}")
            abort(500, message="An error occurred while retrieving the ticket.")

        # Fetch the user based on the username
        user = UserModel.query.filter_by(username=username).first()

        if not user:
            logger.warning(f"User with username {username} not found.")
            abort(404, message="User not found.")

        # Create a new comment using the user ID
        comment = CommentModel(
            ticket_id=ticket_id,
            user_id=user.id,  # Get user ID from the user object
            content=comment_data["content"],
        )

        try:
            # Add the comment to the database
            db.session.add(comment)
            db.session.commit()
            logger.info(f"Created new comment for ticket ID {ticket_id} by user {username}.")
        except SQLAlchemyError as e:
            logger.error(f"Error while saving comment for ticket ID {ticket_id}: {e}")
            abort(500, message="An error occurred while creating the comment.")

        return comment


@blp.route("/comments/<int:comment_id>")
class Comment(MethodView):
    @jwt_required()
    @blp.response(200, CommentSchema)
    def get(self, comment_id):
        """Get a specific comment by ID"""
        logger = current_app.logger
        try:
            logger.info(f"Retrieving comment ID {comment_id}.")
            comment = CommentModel.query.get_or_404(comment_id)
            logger.info(f"Successfully retrieved comment ID {comment_id}.")
            return comment
        except SQLAlchemyError as e:
            logger.error(f"Error while retrieving comment ID {comment_id}: {e}")
            abort(500, message="An error occurred while retrieving the comment.")

    @jwt_required()
    @blp.response(200, {"message": "Comment deleted."})
    def delete(self, comment_id):
        """Delete a specific comment by ID"""
        logger = current_app.logger
        try:
            logger.info(f"Deleting comment ID {comment_id}.")
            comment = CommentModel.query.get_or_404(comment_id)
            db.session.delete(comment)
            db.session.commit()
            logger.info(f"Successfully deleted comment ID {comment_id}.")
        except SQLAlchemyError as e:
            logger.error(f"Error while deleting comment ID {comment_id}: {e}")
            abort(500, message="An error occurred while deleting the comment.")

        return {"message": "Comment deleted."}

    @jwt_required()
    @blp.arguments(PlainCommentSchema)
    @blp.response(200, CommentSchema)
    def put(self, comment_data, comment_id):
        """Update an existing comment by ID"""
        logger = current_app.logger
        try:
            logger.info(f"Updating comment ID {comment_id}.")
            comment = CommentModel.query.get_or_404(comment_id)
        except SQLAlchemyError as e:
            logger.error(f"Error while retrieving comment ID {comment_id}: {e}")
            abort(500, message="An error occurred while retrieving the comment.")

        # Ensure the user trying to update is the one who posted the comment
        user_id = get_jwt_identity()
        if comment.user_id != user_id:
            logger.warning(f"User ID {user_id} is not authorized to update comment ID {comment_id}.")
            abort(403, message="You do not have permission to update this comment.")

        comment.content = comment_data.get("content", comment.content)

        try:
            db.session.commit()
            logger.info(f"Successfully updated comment ID {comment_id}.")
        except SQLAlchemyError as e:
            logger.error(f"Error while updating comment ID {comment_id}: {e}")
            abort(500, message="An error occurred while updating the comment.")

        return comment
