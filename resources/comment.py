from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

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
        ticket = TicketModel.query.get_or_404(ticket_id)
        return ticket.comments  # Return the list of comments for the ticket

    @jwt_required()
    @blp.arguments(CommentSchema)
    @blp.response(201, CommentSchema)
    def post(self, comment_data, ticket_id):
        """Create a new comment on a specific ticket"""
        username = get_jwt_identity()  # Get the username from the JWT token
        ticket = TicketModel.query.get_or_404(ticket_id)  # Fetch the ticket

        # Fetch the user based on the username
        user = UserModel.query.filter_by(username=username).first()

        if not user:
            abort(404, message="User not found.")

        # Create a new comment using the user ID
        comment = CommentModel(
            ticket_id=ticket_id,
            user_id=user.id,  # Get user ID from the user object
            content=comment_data["content"],
        )

        # Add the comment to the database
        db.session.add(comment)
        db.session.commit()

        return comment


@blp.route("/comments/<int:comment_id>")
class Comment(MethodView):
    @jwt_required()
    @blp.response(200, CommentSchema)
    def get(self, comment_id):
        """Get a specific comment by ID"""
        comment = CommentModel.query.get_or_404(comment_id)
        return comment

    @jwt_required()
    @blp.response(200, {"message":"Comment deleted."})
    def delete(self, comment_id):
        """Delete a specific comment by ID"""
        comment = CommentModel.query.get_or_404(comment_id)
        db.session.delete(comment)
        db.session.commit()
        return {"message": "Comment deleted."}

    @jwt_required()
    @blp.arguments(PlainCommentSchema)
    @blp.response(200, CommentSchema)
    def put(self, comment_data, comment_id):
        """Update an existing comment by ID"""
        comment = CommentModel.query.get_or_404(comment_id)

        # Ensure the user trying to update is the one who posted the comment
        user_id = get_jwt_identity()
        if comment.user_id != user_id:
            abort(403, message="You do not have permission to update this comment.")

        comment.content = comment_data.get("content", comment.content)

        try:
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while updating the comment.")

        return comment
