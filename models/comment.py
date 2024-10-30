from db import db


class CommentModel(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    ticket = db.relationship("TicketModel", back_populates="comments")
    user = db.relationship("UserModel", back_populates="comments")