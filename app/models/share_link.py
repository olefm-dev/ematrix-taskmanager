import uuid
import secrets
from datetime import datetime
from app.models import db

class ShareLink(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(64), unique=True, default=lambda: secrets.token_urlsafe(16))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    tasks = db.relationship('Task', backref='share_link', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
