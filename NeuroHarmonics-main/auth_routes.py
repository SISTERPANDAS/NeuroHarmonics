from flask import Blueprint, request, jsonify, session
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__, url_prefix="/api")

@auth.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data received"}), 400

        if User.query.filter_by(email=data.get("email")).first():
            return jsonify({"success": False, "error": "Email already exists"}), 400

        new_user = User(
            username=data.get("fullName"),
            email=data.get("email"),
            password=generate_password_hash(data.get("password")),
            role="user"
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"success": True, "message": "Registration successful"}), 201

    except Exception as e:
        import traceback
        traceback.print_exc()   # ← DO NOT REMOVE
        return jsonify({"success": False, "error": "Server error"}), 500



@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # 1. Fetch the user from Supabase
    user = User.query.filter_by(email=email).first()

    # 2. Check credentials
    if not user or not check_password_hash(user.password, password):
        return jsonify({"success": False, "error": "Invalid email or password"}), 401

    # 3. SET STATUS TO ACTIVE and last login
    user.status = "active"
    if hasattr(user, "last_login_at"):
        from datetime import datetime
        user.last_login_at = datetime.utcnow()

    try:
        db.session.commit()  # Save the "active" status to the database
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Database error"}), 500

    # 4. Set Session Data
    session["user_id"] = user.id
    session["username"] = user.username
    session["role"] = user.role

    return jsonify({"success": True})
