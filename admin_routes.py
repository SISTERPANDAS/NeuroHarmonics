from flask import Blueprint, render_template, session, redirect

admin = Blueprint("admin", __name__, url_prefix="/admin")

@admin.route("/dashboard")
def admin_dashboard():
    if "role" not in session or session["role"] != "admin":
        return redirect("/login")
    return render_template("admin.html")
