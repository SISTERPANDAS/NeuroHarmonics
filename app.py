from flask import Flask, render_template, redirect, session
from models import db
from auth_routes import auth
from admin_routes import admin

app = Flask(__name__)
app.secret_key = "super-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///neuroharmonics.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(admin)


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login.html")
    return render_template("dashboard.html")
# ----------------------------------

@app.route("/")
def home():
    return redirect("/login.html")

if __name__ == "__main__":
    app.run(debug=True)
