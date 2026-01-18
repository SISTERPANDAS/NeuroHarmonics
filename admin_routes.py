from flask import Blueprint, render_template, session, redirect

admin = Blueprint("admin", __name__, url_prefix="/admin")

@admin.route("/dashboard")
def admin_dashboard():
    if "role" not in session or session["role"] != "admin":
        return redirect("/login")
    return render_template("admin.html")

@admin.route("/api/admin-login", methods=["POST"])
def admin_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Look for the admin in the 'admins' table
    admin_user = Admin.query.filter_by(username=username).first()

    if admin_user and check_password_hash(admin_user.password, password):
        session["admin_id"] = admin_user.admin_id
        session["role"] = admin_user.role
        return jsonify({"success": True})

    return jsonify({"success": False, "error": "Invalid Admin Credentials"}), 401