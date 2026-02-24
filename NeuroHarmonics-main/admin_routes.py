"""
Admin control center: dashboard, users, emotion logs, feature toggles, recommendations.
Only role == "admin" can access. All mutations use ORM (no raw SQL).
"""
from functools import wraps
from flask import Blueprint, jsonify, request, redirect, url_for, session, render_template
from models import db, User, Recommendation, SystemLog, EmotionLog, FeatureToggle
from services.admin_service import (
    ensure_feature_toggles,
    get_dashboard_analytics,
    get_user_scan_count,
)

admin = Blueprint("admin", __name__)

PER_PAGE = 20
MAX_PAGE = 100


def admin_required(f):
    """Decorator: require session and role == 'admin'. Return 403 JSON for API, redirect for browser."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            if request.want_json() or request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"error": "Login required"}), 401
            return redirect(url_for("login_page"))
        user = User.query.get(session["user_id"])
        if not user or getattr(user, "role", None) != "admin":
            if request.want_json() or request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"error": "Admin access required"}), 403
            return redirect(url_for("home"))
        # Optional: respect is_active
        if getattr(user, "is_active", True) is False:
            if request.want_json():
                return jsonify({"error": "Account disabled"}), 403
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return wrapped


# --- Dashboard (HTML + analytics) ---
@admin.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    ensure_feature_toggles()
    analytics = get_dashboard_analytics()
    return render_template("admin/admin_dashboard.html", analytics=analytics)


# --- Stats API (backward compatible) ---
@admin.route("/admin/stats")
@admin_required
def admin_stats():
    a = get_dashboard_analytics()
    return jsonify({
        "users": a["total_users"],
        "uploads": SystemLog.query.filter_by(level="UPLOAD").count(),
        "alerts": SystemLog.query.filter_by(level="ALERT").count(),
        "total_emotion_scans": a["total_emotion_scans"],
        "most_common_emotion": a["most_common_emotion"],
        "active_sessions": a["active_sessions"],
    })


# --- User management ---
@admin.route("/admin/users")
@admin_required
def get_users():
    page = request.args.get("page", 1, type=int)
    page = max(1, min(page, MAX_PAGE))
    pagination = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=PER_PAGE)
    users = []
    for u in pagination.items:
        users.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role or "user",
            "status": u.status,
            "is_active": getattr(u, "is_active", True),
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else None,
            "total_scans": get_user_scan_count(u.id),
        })
    return jsonify({
        "users": users,
        "total": pagination.total,
        "page": page,
        "per_page": PER_PAGE,
        "pages": pagination.pages,
    })


@admin.route("/admin/user/<int:user_id>")
@admin_required
def get_user_detail(user_id):
    u = User.query.get_or_404(user_id)
    emotion_logs = EmotionLog.query.filter_by(user_id=u.id).order_by(EmotionLog.created_at.desc()).limit(10).all()
    return jsonify({
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "role": u.role or "user",
        "status": u.status,
        "is_active": getattr(u, "is_active", True),
        "created_at": u.created_at.isoformat() if u.created_at else None,
        "last_login_at": u.last_login_at.isoformat() if getattr(u, "last_login_at", None) else None,
        "total_scans": get_user_scan_count(u.id),
        "emotion_history": [
            {"id": e.id, "dominant_emotion": e.dominant_emotion, "confidence_score": e.confidence_score, "created_at": e.created_at.isoformat() if e.created_at else None}
            for e in emotion_logs
        ],
    })


@admin.route("/admin/user/<int:user_id>/update", methods=["POST"])
@admin_required
def update_user(user_id):
    u = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    # Validate: no raw SQL, use ORM only
    if "username" in data and isinstance(data["username"], str):
        name = (data["username"] or "").strip()
        if name and len(name) <= 100:
            u.username = name
    if "email" in data and isinstance(data["email"], str):
        email = (data["email"] or "").strip()
        if email and len(email) <= 120:
            existing = User.query.filter(User.email == email, User.id != user_id).first()
            if not existing:
                u.email = email
    if "role" in data and data["role"] in ("admin", "user"):
        u.role = data["role"]
    if "is_active" in data:
        u.is_active = bool(data["is_active"])
    db.session.commit()
    return jsonify({"success": True})


@admin.route("/admin/user/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    u = User.query.get_or_404(user_id)
    u.is_active = False
    u.status = "inactive"
    db.session.commit()
    return jsonify({"success": True, "message": "User deactivated (soft delete)"})


# --- Emotion log management ---
@admin.route("/admin/emotions")
@admin_required
def get_emotions():
    page = request.args.get("page", 1, type=int)
    page = max(1, min(page, MAX_PAGE))
    q = EmotionLog.query
    emotion_type = request.args.get("emotion", "").strip()
    if emotion_type:
        q = q.filter(EmotionLog.dominant_emotion == emotion_type)
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()
    if date_from:
        try:
            from datetime import datetime
            q = q.filter(EmotionLog.created_at >= datetime.fromisoformat(date_from.replace("Z", "+00:00")))
        except ValueError:
            pass
    if date_to:
        try:
            from datetime import datetime
            q = q.filter(EmotionLog.created_at <= datetime.fromisoformat(date_to.replace("Z", "+00:00")))
        except ValueError:
            pass
    min_confidence = request.args.get("min_confidence", type=float)
    if min_confidence is not None:
        q = q.filter(EmotionLog.confidence_score >= min_confidence)
    q = q.order_by(EmotionLog.created_at.desc())
    pagination = q.paginate(page=page, per_page=PER_PAGE)
    items = []
    for e in pagination.items:
        items.append({
            "id": e.id,
            "user_id": e.user_id,
            "username": e.user.username if e.user else None,
            "dominant_emotion": e.dominant_emotion,
            "confidence_score": e.confidence_score,
            "created_at": e.created_at.strftime("%Y-%m-%d %H:%M") if e.created_at else None,
        })
    return jsonify({
        "emotions": items,
        "total": pagination.total,
        "page": page,
        "per_page": PER_PAGE,
        "pages": pagination.pages,
    })


@admin.route("/admin/emotion/<int:log_id>/delete", methods=["POST"])
@admin_required
def delete_emotion_log(log_id):
    e = EmotionLog.query.get_or_404(log_id)
    db.session.delete(e)
    db.session.commit()
    return jsonify({"success": True})


# --- Feature toggles ---
@admin.route("/admin/features")
@admin_required
def get_features():
    ensure_feature_toggles()
    toggles = FeatureToggle.query.order_by(FeatureToggle.feature_name).all()
    return jsonify({
        "features": [{"id": t.id, "feature_name": t.feature_name, "is_enabled": t.is_enabled} for t in toggles]
    })


@admin.route("/admin/features/update", methods=["POST"])
@admin_required
def update_features():
    data = request.get_json() or {}
    if not isinstance(data.get("features"), list):
        return jsonify({"error": "Expected { features: [{ feature_name, is_enabled }] }"}), 400
    for item in data["features"]:
        name = item.get("feature_name") if isinstance(item, dict) else None
        if not name or not isinstance(name, str) or len(name) > 80:
            continue
        enabled = bool(item.get("is_enabled", True)) if isinstance(item, dict) else True
        t = FeatureToggle.query.filter_by(feature_name=name).first()
        if t:
            t.is_enabled = enabled
        else:
            db.session.add(FeatureToggle(feature_name=name, is_enabled=enabled))
    db.session.commit()
    return jsonify({"success": True})


# --- Recommendation mappings ---
@admin.route("/admin/recommendations")
@admin_required
def list_recommendations():
    # Return emotion -> content mappings (group by emotion, latest content)
    recs = Recommendation.query.order_by(Recommendation.emotion, Recommendation.id.desc()).all()
    seen = set()
    mappings = []
    for r in recs:
        if r.emotion and r.emotion not in seen:
            seen.add(r.emotion)
            mappings.append({"emotion": r.emotion, "content": r.content or ""})
    return jsonify({"recommendations": mappings})


@admin.route("/admin/recommendations/update", methods=["POST"])
@admin_required
def update_recommendations():
    data = request.get_json() or {}
    if not isinstance(data.get("recommendations"), list):
        return jsonify({"error": "Expected { recommendations: [{ emotion, content }] }"}), 400
    for item in data["recommendations"]:
        if not isinstance(item, dict):
            continue
        emotion = (item.get("emotion") or "").strip().lower()
        content = (item.get("content") or "").strip()
        if not emotion or len(emotion) > 50:
            continue
        existing = Recommendation.query.filter_by(emotion=emotion).first()
        if existing:
            existing.content = content
        else:
            db.session.add(Recommendation(emotion=emotion, content=content))
    db.session.commit()
    return jsonify({"success": True})


# --- Legacy: add recommendation (backward compatible) ---
@admin.route("/admin/recommendations", methods=["POST"])
@admin_required
def add_recommendation():
    data = request.get_json() or {}
    emotion = (data.get("emotion") or "").strip()
    content = (data.get("content") or "").strip()
    if not emotion or len(emotion) > 50:
        return jsonify({"error": "Invalid emotion"}), 400
    rec = Recommendation(emotion=emotion, content=content)
    db.session.add(rec)
    db.session.commit()
    return jsonify({"success": True})


# --- Logs ---
@admin.route("/admin/logs")
@admin_required
def get_logs():
    logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).limit(50).all()
    return jsonify([
        {"message": l.message, "level": l.level, "time": l.timestamp.strftime("%Y-%m-%d %H:%M") if l.timestamp else None}
        for l in logs
    ])
