from datetime import datetime

from app import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    phone = db.Column(db.String(20), nullable = True)
    email = db.Column(db.String(150), unique= True, nullable= False)
    password_hash = db.Column(db.String(255), nullable= False)
    role = db.Column(db.String(20), default= "user")
    created_at = db.Column(db.DateTime, default = datetime.utcnow)
