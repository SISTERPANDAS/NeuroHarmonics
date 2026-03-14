from flask import Blueprint, jsonify, request, session, redirect, render_template
from models import User, Recommendation, SystemLog, get_users_collection
from werkzeug.security import check_password_hash
import re

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
    Expects JSON: { "email": "...", "password": "..." }
    Validates against users with role='admin'.
    """
    try:
        data = request.get_json() or {}
        identity = (data.get("email") or data.get("username") or "").strip()
        password = data.get("password")

        if not identity or not password:
            return jsonify({"success": False, "message": "Email and password required"}), 400

        # Attempt to find admin by email or username, case-insensitive fallback
        admin_user = get_users_collection().find_one({
            "role": "admin",
            "$or": [
                {"email": identity},
                {"username": identity},
                {"email": {"$regex": f"^{re.escape(identity)}$", "$options": "i"}},
                {"username": {"$regex": f"^{re.escape(identity)}$", "$options": "i"}}
            ]
        })

        if not admin_user or not check_password_hash(admin_user.get("password", ""), password):
            return jsonify({"success": False, "message": "Invalid admin credentials"}), 401

        session["user_id"] = str(admin_user["_id"])
        session["username"] = admin_user.get("username", identity)
        session["role"] = "admin"

        return jsonify({"success": True, "redirect": "/admin"})
    except Exception:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": "Server error during admin login"}), 500

# 🔐 Dashboard stats
@admin.route("/admin/stats")
def admin_stats():
    return jsonify({
        "users": User.count(),
        "uploads": SystemLog.count_by_level("UPLOAD"),
        "alerts": SystemLog.count_by_level("ALERT")
    })

# 👥 Users
@admin.route("/admin/users")
def get_users():
    try:
        users = User.get_all()
        return jsonify([
            {"id": str(u["_id"]), "name": u.get("username", ""), "role": u.get("role", "user"), "status": u.get("status", "active")}
            for u in users
        ])
    except Exception as e:
        print(f"Error getting users: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# 🧠 Recommendations
@admin.route("/admin/recommendations", methods=["POST"])
def add_recommendation():
    try:
        data = request.json
        rec_id = Recommendation.create(
            emotion=data.get("emotion", ""),
            content=data.get("content", "")
        )
        return jsonify({"success": True, "id": rec_id})
    except Exception as e:
        print(f"Error adding recommendation: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# 📜 Logs
@admin.route("/admin/logs")
def get_logs():
    try:
        logs = SystemLog.get_recent(limit=50)
        return jsonify([
            {
                "message": l.get("message", ""),
                "level": l.get("level", "INFO"),
                "time": l.get("timestamp", "").isoformat() if hasattr(l.get("timestamp", ""), "isoformat") else str(l.get("timestamp", ""))
            } for l in logs
        ])
    except Exception as e:
        print(f"Error getting logs: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

