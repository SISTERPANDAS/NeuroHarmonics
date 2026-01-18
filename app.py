from flask import Flask, render_template, redirect, session
from models import db
from auth_routes import auth
from admin_routes import admin   # ✅ you have this

app = Flask(__name__)
app.secret_key = "super-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///neuroharmonics.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(admin)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return redirect("index/index.html")

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("index/login.html")   # 🔴 FIXED

@app.route("/register", methods=["GET"])
def register_page():
    return render_template("index/login.html")  # 🔴 FIXED

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("dashboard/dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)
