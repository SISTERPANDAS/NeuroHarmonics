from flask import Blueprint, jsonify, request, session, redirect, render_template
from models import db, User, Recommendation, SystemLog

admin = Blueprint("admin", __name__)


@admin.route("/admin-login-page", methods=["GET"])
def admin_login_page():
    """
    Simple admin login page used when clicking 'Login as Admin' from the main login screen.
    """
    return render_template("admin/admin_login.html")


@admin.route("/admin-login", methods=["POST"])
def admin_login():
    """
    Admin-only login.
    Expects JSON: { "username": "...", "password": "..." }
    Validates against users with role='admin'.
    """
    try:
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"success": False, "message": "Username and password required"}), 400

        # Here we treat admin records as regular users with role='admin'.
        # Password is stored hashed using the same mechanism as normal users.
        from werkzeug.security import check_password_hash

        admin_user = User.query.filter_by(username=username, role="admin").first()
        if not admin_user or not check_password_hash(admin_user.password, password):
            return jsonify({"success": False, "message": "Invalid admin credentials"}), 401

        session["user_id"] = admin_user.id
        session["username"] = admin_user.username
        session["role"] = admin_user.role

        return jsonify({"success": True, "redirect": "/admin"})
    except Exception:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": "Server error during admin login"}), 500

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
