from flask import Blueprint, jsonify, request
from models import db, User, Recommendation, SystemLog

admin = Blueprint("admin", __name__)

# 🔐 Dashboard stats
@admin.route("/admin/stats")
def admin_stats():
    return jsonify({
        "users": User.query.count(),
        "uploads": SystemLog.query.filter_by(level="UPLOAD").count(),
        "alerts": SystemLog.query.filter_by(level="ALERT").count()
    })

# 👥 Users
@admin.route("/admin/users")
def get_users():
    users = User.query.all()
    return jsonify([
        {"id": u.id, "name": u.name, "role": u.role, "status": u.status}
        for u in users
    ])

# 🧠 Recommendations
@admin.route("/admin/recommendations", methods=["POST"])
def add_recommendation():
    data = request.json
    rec = Recommendation(
        emotion=data["emotion"],
        content=data["content"]
    )
    db.session.add(rec)
    db.session.commit()
    return jsonify({"success": True})

# 📜 Logs
@admin.route("/admin/logs")
def get_logs():
    logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).limit(50)
    return jsonify([
        {
            "message": l.message,
            "level": l.level,
            "time": l.timestamp.strftime("%Y-%m-%d %H:%M")
        } for l in logs
    ])
