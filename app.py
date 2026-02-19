from flask import Flask, render_template, redirect, session, request, url_for, flash, jsonify
from models import db, Feedback, ContactMessage, User, CommunityMessage # Added CommunityMessage
from auth_routes import auth
from admin_routes import admin 
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super-secret-key"

# Supabase Connection
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:06kingbeast#2328@db.pqeiqbqqrmzrkgeqrlkv.supabase.co:5432/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(admin)

# --- Routes ---

@app.route("/")
def home():
    # Multi-level sort: 1. Highest Rating, 2. Newest (by ID)
    feedbacks = db.session.query(Feedback, User.username)\
                  .join(User, Feedback.user_id == User.id)\
                  .filter(Feedback.rating >= 4)\
                  .order_by(Feedback.rating.desc(), Feedback.id.desc())\
                  .limit(15).all() 
    
    return render_template("index/index.html", feedbacks=feedbacks)

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("index/login.html")  

@app.route("/register", methods=["GET"])
def register_page():
    return render_template("index/login.html")

# MERGED DASHBOARD ROUTE (Fixed the duplicate error)
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")
    
    user_name = session.get("username", "Guest User")
    
    # Fetch Community Messages for the chat tab
    messages = CommunityMessage.query.order_by(CommunityMessage.timestamp.asc()).limit(50).all()
    
    return render_template("dashboard/dashboard.html", 
                           username=user_name, 
                           community_messages=messages)

@app.route("/admin")
def admin_page():
    return render_template("admin/admin.html")

@app.route("/health-tips")
def health_tips():
    return render_template("index/health_tips.html")

@app.route("/logout")
def logout():
    # 1. Get the user ID from the session before clearing it
    user_id = session.get("user_id")
    
    if user_id:
        # 2. Find the user in the database
        user = User.query.get(user_id)
        if user:
            # 3. Change status to inactive
            user.status = "inactive"
            db.session.commit()
    
    # 4. Wipe the session clean
    session.clear()
    return redirect("/login")

# --- Form Submissions ---

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user = User.query.filter_by(username=session['username']).first()
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    
    if user:
        new_feedback = Feedback(user_id=user.id, rating=rating, comment=comment)
        db.session.add(new_feedback)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "User not found"}), 404

@app.route('/send-message', methods=['POST'])
def send_message():
    user = User.query.filter_by(username=session.get('username')).first()
    user_id = user.id if user else None
    
    new_message = ContactMessage(
        user_id=user_id,
        name=session.get('username', 'Guest'),
        email=user.email if user else "guest@example.com",
        subject=request.form.get('subject'),
        message=request.form.get('message')
    )
    db.session.add(new_message)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/post-community', methods=['POST'])
def post_community():
    data = request.get_json()
    if 'username' in session and data.get('message'):
        new_msg = CommunityMessage(
            username=session['username'],
            content=data['message']
        )
        db.session.add(new_msg)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Unauthorized"}), 401

if __name__ == "__main__":
    with app.app_context():
        db.create_all() # Ensures all tables (including Community) exist in Supabase
    app.run(debug=True)
