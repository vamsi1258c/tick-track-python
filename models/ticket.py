from db import db

class TicketModel(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')
    priority = db.Column(db.String(20), default='medium')
    category = db.Column(db.String(100), default='ALL')
    subcategory = db.Column(db.String(100), default='ALL')
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, onupdate=db.func.current_timestamp())

    creator = db.relationship("UserModel", back_populates="tickets_created", foreign_keys=[created_by])
    assignee = db.relationship("UserModel", back_populates="tickets_assigned", foreign_keys=[assigned_to])
    approver = db.relationship("UserModel", back_populates="tickets_approved", foreign_keys=[approved_by])
    comments = db.relationship("CommentModel", back_populates="ticket", cascade="all, delete-orphan")
    activity_logs = db.relationship("ActivityLogModel", back_populates="ticket", cascade="all, delete-orphan")
    attachments = db.relationship("AttachmentModel", back_populates="ticket", cascade="all, delete-orphan")
