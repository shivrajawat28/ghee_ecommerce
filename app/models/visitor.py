from app import db
from datetime import datetime

class Visitor(db.Model):
    __tablename__ = "visitor"

    id = db.Column(db.Integer, primary_key = True)
    ip_address = db.Column(db.String(50))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    visited_at = db.Column(db.DateTime, default = datetime.utcnow)