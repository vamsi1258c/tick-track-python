# user_model.py

from db import db


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String(50), nullable=True)
    designation = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(20), nullable=True)
    approver = db.Column(db.Boolean, default=False, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, onupdate=db.func.current_timestamp())

    tickets_created = db.relationship("TicketModel", back_populates="creator", foreign_keys="TicketModel.created_by")
    tickets_assigned = db.relationship("TicketModel", back_populates="assignee", foreign_keys="TicketModel.assigned_to")
    tickets_approved = db.relationship("TicketModel", back_populates="approver", foreign_keys="TicketModel.approved_by")
    comments = db.relationship("CommentModel", back_populates="user",
                               cascade="all, delete-orphan")  # Comments made by the user
    activity_logs = db.relationship("ActivityLogModel", back_populates="user",
                                    cascade="all, delete-orphan")  # Activity logs related to the user

