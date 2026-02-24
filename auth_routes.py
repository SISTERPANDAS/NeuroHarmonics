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

@auth.route("/admin-login-page")
def admin_login_page():
    # Make sure 'admin_login.html' is inside your 'templates/index/' folder
    return render_template("index/admin_login.html")


@auth.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    # Query the 'admins' table instead of 'users'
    admin = Admin.query.filter_by(username=data.get('username')).first()

    if admin and admin.password == data.get('password'):  # Note: Use hashing in production
        session['username'] = admin.username
        session['admin_id'] = admin.admin_id
        session['role'] = 'admin'
        
        return jsonify({"success": True, "redirect": url_for('admin_panel')})
    
    return jsonify({"success": False, "message": "Invalid Admin Credentials"}), 401

@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    image_data = data.get("face_image")  # base64 image from frontend

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"success": False, "error": "Invalid email or password"}), 401

    user.status = "active"
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Database error"}), 500

    session["user_id"] = user.id
    session["username"] = user.username
    session["role"] = user.role

    # Live emotion detection
    emotion_result = None
    accuracy = None
    if image_data:
        # Call emotion detection backend
        import requests
        res = requests.post("http://localhost:8000/predict", json={"image": image_data})
        if res.status_code == 200:
            result = res.json()
            emotion_result = result.get("emotion")
            accuracy = result.get("accuracy")
            # Optionally log emotion
            from models import EmotionLog
            from datetime import datetime
            log = EmotionLog(
                user_id=user.id,
                emotion=emotion_result,
                timestamp=datetime.utcnow()
            )
            db.session.add(log)
            db.session.commit()

    return jsonify({"success": True, "emotion": emotion_result, "accuracy": accuracy})
