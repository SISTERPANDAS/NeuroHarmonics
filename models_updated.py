from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    password = db.Column(db.String(255), nullable=False)
    dob = db.Column(db.Date)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    avatar = db.Column(db.Text)
    role = db.Column(db.String(20), default="user")
    status = db.Column(db.String(20), default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    feedbacks = db.relationship('Feedback', backref='user', lazy=True, cascade='all, delete-orphan')
    eeg_sessions = db.relationship('EEGSession', backref='user', lazy=True, cascade='all, delete-orphan')
    monthly_reports = db.relationship('MonthlyReport', backref='user', lazy=True, cascade='all, delete-orphan')
    emotion_logs = db.relationship('EmotionLog', backref='user', lazy=True, cascade='all, delete-orphan')
    contact_messages = db.relationship('ContactMessage', backref='user', lazy=True, cascade='all, delete-orphan')
    community_message = db.relationship('CommunityMessage', backref='user', lazy=True, cascade='all, delete-orphan')
    recommendations = db.relationship('Recommendation', backref='user', lazy=True, cascade='all, delete-orphan')


class Admin(db.Model):
    __tablename__ = 'admins'

    admin_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='admin')
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    activities_created = db.relationship('Activity', foreign_keys='Activity.created_by', backref='creator', lazy=True)
    activities_updated = db.relationship('Activity', foreign_keys='Activity.updated_by', backref='updater', lazy=True)
    feedbacks_reviewed = db.relationship('Feedback', backref='reviewer', lazy=True)
    contact_replies = db.relationship('ContactMessage', backref='admin_responder', lazy=True)


class Activity(db.Model):
    __tablename__ = 'activities'

    activity_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(30), nullable=False)  # yoga, music, meditation, breathing, article, video
    description = db.Column(db.Text)
    file_path = db.Column(db.Text)
    playlist_url = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer)
    difficulty_level = db.Column(db.String(20), default='beginner')
    target_emotions = db.Column(db.String(255))
    tags = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('admins.admin_id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('admins.admin_id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    eeg_sessions = db.relationship('EEGSession', backref='activity', lazy=True)
    feedbacks = db.relationship('Feedback', backref='activity', lazy=True)
    recommendations = db.relationship('Recommendation', backref='activity', lazy=True)


class EEGSession(db.Model):
    __tablename__ = 'eeg_sessions'

    session_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_type = db.Column(db.String(20), nullable=False)  # baseline, activity, monitoring
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)
    emotion_label = db.Column(db.String(50))
    emotion_confidence = db.Column(db.Float)
    raw_eeg_data = db.Column(db.Text)
    chosen_activity_id = db.Column(db.Integer, db.ForeignKey('activities.activity_id'), nullable=True)
    notes = db.Column(db.Text)
    is_complete = db.Column(db.Boolean, default=False)

    # Relationships
    feedbacks = db.relationship('Feedback', backref='session', lazy=True)


class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    feedback_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('eeg_sessions.session_id'), nullable=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.activity_id'), nullable=True)
    rating = db.Column(db.SmallInteger, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    is_helpful = db.Column(db.Boolean)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('admins.admin_id'), nullable=True)
    admin_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)


class MonthlyReport(db.Model):
    __tablename__ = 'monthly_reports'

    report_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    dominant_emotion = db.Column(db.String(50))
    total_sessions = db.Column(db.Integer, default=0)
    negative_count = db.Column(db.Integer, default=0)
    positive_count = db.Column(db.Integer, default=0)
    neutral_count = db.Column(db.Integer, default=0)
    avg_emotion_score = db.Column(db.Float)
    flagged_for_therapist = db.Column(db.Boolean, default=False)
    therapist_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)


class EmotionLog(db.Model):
    __tablename__ = 'emotion_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    emotion = db.Column(db.String(50), nullable=False)
    intensity = db.Column(db.SmallInteger)  # 1-10
    trigger = db.Column(db.Text)
    activity_type = db.Column(db.String(30))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False)
    admin_reply = db.Column(db.Text)
    replied_by = db.Column(db.Integer, db.ForeignKey('admins.admin_id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    replied_at = db.Column(db.DateTime)


class CommunityMessage(db.Model):
    __tablename__ = 'community_message'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    is_flagged = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)


class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    emotion = db.Column(db.String(50), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.activity_id'), nullable=True)
    content = db.Column(db.Text)
    reason = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SystemLog(db.Model):
    __tablename__ = 'system_logs'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(20))  # INFO, WARNING, ERROR, DEBUG
    module = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    metadata = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
