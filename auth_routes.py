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

    user = User.query.filter_by(email=data.get("email")).first()

    if not user or not check_password_hash(user.password, data.get("password")):
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

    session["user_id"] = user.id
    session["username"] = user.username
    session["role"] = user.role

    return jsonify({"success": True})
