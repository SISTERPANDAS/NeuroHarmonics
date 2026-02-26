from flask import Blueprint, request, jsonify, session
from models import db, User
from werkzeug.security import check_password_hash, generate_password_hash

auth = Blueprint("auth", __name__, url_prefix="/api")

@auth.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return jsonify({"success": False, "error": "Email and password required"}), 400
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({"success": False, "error": "Invalid email or password"}), 401
        username = user.username if user.username else (user.email.split('@')[0] if user.email else "User")
        session["user_id"] = user.id
        session["username"] = username
        session["role"] = user.role
        user.status = "active"
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return jsonify({"success": False, "error": "Database error"}), 500
        return jsonify({"success": True, "username": username})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": "Server error"}), 500


@auth.route("/register", methods=["POST"])
def register():
    """
    Register a new regular user.
    Expects JSON: { "fullName": "...", "email": "...", "password": "..." }
    """
    try:
        data = request.get_json() or {}
        full_name = data.get("fullName")
        email = data.get("email")
        password = data.get("password")

        if not full_name or not email or not password:
            return jsonify({"success": False, "error": "Name, email and password are required"}), 400

        existing = User.query.filter_by(email=email).first()
        if existing:
            return jsonify({"success": False, "error": "Email already registered"}), 400

        hashed = generate_password_hash(password)
        user = User(
            username=full_name,
            email=email,
            password=hashed,
            role="user",
        )
        db.session.add(user)
        db.session.commit()

        # Log the user in immediately after registration
        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] = user.role

        return jsonify({"success": True, "username": user.username})
    except Exception:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"success": False, "error": "Server error during registration"}), 500
