from flask import Flask, render_template, redirect, session
from models import db
from auth_routes import auth
from admin_routes import admin 

app = Flask(__name__)
app.secret_key = "super-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:06kingbeast#2328@db.pqeiqbqqrmzrkgeqrlkv.supabase.co:5432/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(admin)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index/index.html")

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("index/login.html")  

@app.route("/register", methods=["GET"])
def register_page():
    return render_template("index/login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    user_name = session.get("username", "Guest User")
    return render_template("dashboard/dashboard.html", username=user_name)

@app.route("/admin")
def admin_page():
    return render_template("admin/admin.html")

@app.route("/health-tips")
def health_tips():
    # Renders the new page we are about to create
    return render_template("index/health_tips.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

