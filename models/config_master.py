from db import db

class ConfigMasterModel(db.Model):
    __tablename__ = "config_master"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'status', 'category', 'subcategory', 'priority'
    value = db.Column(db.String(100), nullable=False)
    label = db.Column(db.String(100), nullable=False)  # Display label for UI (optional)
    color = db.Column(db.String(20), nullable=True)    # Hex code or predefined colors for UI badges (optional)
    parent = db.Column(db.String(50), nullable=True)   # Optional parent
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, onupdate=db.func.current_timestamp())
