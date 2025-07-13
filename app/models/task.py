from datetime import datetime
from app.models import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    quadrant = db.Column(db.Integer, default=1)
    completed = db.Column(db.Boolean, default=False)
    is_requested = db.Column(db.Boolean, default=False)
    share_link_id = db.Column(db.String(36), db.ForeignKey('share_link.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
