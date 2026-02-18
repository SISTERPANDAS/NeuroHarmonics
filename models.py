from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), default="user")
    status = db.Column(db.String(20), default="active")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emotion = db.Column(db.String(50))
    content = db.Column(db.Text)

class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    level = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
