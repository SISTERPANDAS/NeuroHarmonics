from flask import Flask, render_template, redirect, session, request, url_for, flash, jsonify
from models import db, Feedback, ContactMessage, User, CommunityMessage
from face_routes import face
from auth_routes import auth
from admin_routes import admin
import os
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = "super-secret-key"

# Database Connection - Use local SQLite by default
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///neuroharmonics.db",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(face)

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

# MERGED DASHBOARD ROUTE
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
    # List of video files and their corresponding thumbnails
    all_videos = [
        {
            'title': 'Spending Time Happily',
            'video': 'spending_time_happily.mp4',
            'thumb': 'spending_time_happily.jpg',
            'quote': 'Happiness is not by chance, but by choice.',
            'tip': 'Spend time with loved ones and cherish every moment.'
        },
        {
            'title': 'Relaxed Time',
            'video': 'relaxed_time.mp4',
            'thumb': 'relaxed_time.jpg',
            'quote': 'Relaxation is the key to a peaceful mind.',
            'tip': 'Take a deep breath and let your worries melt away.'
        },
        {
            'title': 'Happy Activities',
            'video': 'happy_activities.mp4',
            'thumb': 'happy_activities.jpg',
            'quote': 'Do more of what makes you happy.',
            'tip': 'Engage in activities that bring you joy and fulfillment.'
        },
        {
            'title': 'Promise to a Friend',
            'video': 'promise_to_a_friend.mp4',
            'thumb': 'promise_to_a_friend.jpg',
            'quote': 'A promise made is a trust earned.',
            'tip': 'Keep your promises and strengthen your bonds.'
        },
        {
            'title': 'Body Movements',
            'video': 'body_movements.mp4',
            'thumb': 'body_movements.jpg',
            'quote': 'Movement is a medicine for creating change.',
            'tip': 'Move your body daily to boost your mood and energy.'
        },
        {
            'title': 'Create a New Morning Routine',
            'video': 'Create_a_new_morning_routine.mp4',
            'thumb': 'create_a_new_morning_routine.jpg',
            'quote': 'Win the morning, win the day.',
            'tip': 'Start your day with a positive and healthy routine.'
        },
        {
            'title': 'Finding Goal',
            'video': 'finding_goal.mp4',
            'thumb': 'finding_goal.jpg',
            'quote': 'Set your goals high, and don’t stop till you get there.',
            'tip': 'Define your purpose and take steps toward your dreams.'
        },
    ]
    videos = random.sample(all_videos, 4) if len(all_videos) >= 4 else all_videos
    return render_template(
        "index/health_tips.html",
        videos=videos
    )

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
        db.create_all()
    app.run(debug=True)

