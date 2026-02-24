"""
Admin helper functions: analytics, feature defaults, validation.
"""
from sqlalchemy import func
from models import db, User, EmotionLog, FeatureToggle, Recommendation

# Default feature toggles (created if missing)
DEFAULT_FEATURES = [
    ("face_scan_enabled", True),
    ("recommendation_engine_enabled", True),
    ("quotes_api_enabled", True),
]


def ensure_feature_toggles():
    """Ensure default feature toggles exist in DB."""
    for name, enabled in DEFAULT_FEATURES:
        if not FeatureToggle.query.filter_by(feature_name=name).first():
            db.session.add(FeatureToggle(feature_name=name, is_enabled=enabled))
    db.session.commit()


def get_dashboard_analytics():
    """Return summary for admin dashboard."""
    total_users = User.query.count()
    total_scans = EmotionLog.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    # Most common emotion
    most_common = (
        db.session.query(EmotionLog.dominant_emotion, func.count(EmotionLog.id))
        .group_by(EmotionLog.dominant_emotion)
        .order_by(func.count(EmotionLog.id).desc())
        .first()
    )
    most_common_emotion = most_common[0] if most_common else "—"
    # "Active sessions" = users with status active (we don't track real sessions)
    active_sessions = User.query.filter_by(status="active").count()
    return {
        "total_users": total_users,
        "total_emotion_scans": total_scans,
        "most_common_emotion": most_common_emotion,
        "active_sessions": active_sessions,
        "active_users": active_users,
    }


def get_user_scan_count(user_id):
    """Return total emotion scans for a user."""
    return EmotionLog.query.filter_by(user_id=user_id).count()


def is_feature_enabled(feature_name):
    """Check if a feature is enabled (for use in app/face_routes)."""
    row = FeatureToggle.query.filter_by(feature_name=feature_name).first()
    return row.is_enabled if row else True
