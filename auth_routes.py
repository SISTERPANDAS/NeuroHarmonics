from flask import Blueprint, request, jsonify, session
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__, url_prefix="/api")

@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid data"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(
        full_name=data["fullName"],
        email=data["email"],
        password=generate_password_hash(data["password"])
    )

    from models import db
    db.session.add(user)
    db.session.commit()

    return jsonify({"success": True})


@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_id"] = user.id
    return jsonify({"success": True})