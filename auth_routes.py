from flask import Blueprint, request, jsonify, session
from models import User
from werkzeug.security import check_password_hash, generate_password_hash
import re

auth = Blueprint("auth", __name__, url_prefix="/api")

# Validation helpers
def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_strong_password(password):
    """Validate password strength (min 8 chars, alphanumeric)"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letters"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain numbers"
    return True, "Valid"

@auth.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return jsonify({"success": False, "error": "Email and password required"}), 400
        
        # Try finding user by email first
        user = User.find_by_email(email)
        # If not found, try by username
        if not user:
            user = User.find_by_username(email)
            
        if not user or not check_password_hash(user["password"], password):
            return jsonify({"success": False, "error": "Invalid email or password"}), 401
        
        username = user.get("username") if user.get("username") else (email.split('@')[0] if email else "User")
        session["user_id"] = str(user["_id"])
        session["username"] = username
        role = user.get("role", "user")
        session["role"] = role
        session.permanent = True
        
        # Update user status to active
        try:
            User.update_status(str(user["_id"]), "active")
        except Exception:
            pass  # Ignore status update errors

        redirect_url = "/admin" if role == "admin" else "/dashboard"
        return jsonify({"success": True, "username": username, "redirect": redirect_url})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": "Server error"}), 500


@auth.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json() or {}
        fullName = data.get("fullName") or data.get("full_name") or data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not fullName or not email or not password:
            return jsonify({"success": False, "error": "All fields required"}), 400

        # Validate email format
        if not is_valid_email(email):
            return jsonify({"success": False, "error": "Invalid email format"}), 400

        # Validate password strength
        is_strong, msg = is_strong_password(password)
        if not is_strong:
            return jsonify({"success": False, "error": msg}), 400

        # Validate fullName (alphanumeric + spaces)
        if not re.match(r'^[a-zA-Z\s]+$', fullName):
            return jsonify({"success": False, "error": "Name must contain only letters and spaces"}), 400

        # Prevent duplicate emails
        if User.find_by_email(email):
            return jsonify({"success": False, "error": "Email already registered"}), 400

        hashed = generate_password_hash(password)
        user_id = User.create(
            username=fullName.strip(),
            email=email.strip(),
            password=hashed,
            role="user",
            status="active"
        )

        # Auto-login after registration
        session["user_id"] = user_id
        session["username"] = fullName.strip()
        session["role"] = "user"
        session.permanent = True

        return jsonify({"success": True, "username": fullName.strip()})
    except Exception:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": "Server error"}), 500
