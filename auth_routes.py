from flask import Blueprint, request, jsonify, session
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__, url_prefix="/api")

@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    # Use .get() to avoid errors if a field is missing
    new_user = User(
        username=data.get("fullName"), # Map 'fullName' from JS to 'username' in DB
        email=data.get("email"),
        password=generate_password_hash(data.get("password")),
        gender=data.get("gender")      # Added based on your DB schema
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": True}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()

    if user and check_password_hash(user.password, data.get("password")):
        # YOU MUST ADD THIS LINE
        session["user_id"] = user.user_id
        session["username"] = user.username # This matches line 35 in your HTML
        
        return jsonify({"success": True})
    
    return jsonify({"success": False, "error": "Invalid credentials"}), 401