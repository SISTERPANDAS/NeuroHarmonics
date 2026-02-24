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
    for v in videos:
        v['video_path'] = 'videos/' + v['video']
    
    # Time-based music recommendations
    current_hour = datetime.now().hour
    
    # Determine time period: 4am-12pm = morning, 12pm-10pm = evening, 10pm-4am = night
    if 4 <= current_hour < 12:
        time_period = 'morning'
        time_greeting = 'Good Morning'
        quotes = [
            'Rise and shine! Every morning is a new opportunity.',
            'The early bird catches the worm - start your day with intention.',
            'Morning is the wick, the day is the candle.',
            'Today is a new day. Make it count!'
        ]
    elif 12 <= current_hour < 22:
        time_period = 'evening'
        time_greeting = 'Good Evening'
        quotes = [
            'The evening brings everything in moderation.',
            'Every sunset is an opportunity to reset.',
            'Evenings are for reflection and gratitude.',
            'Finish strong - make the most of your evening!'
        ]
    else:
        time_period = 'night'
        time_greeting = 'Good Night'
        quotes = [
            'Sweet dreams are made of this.',
            'Rest is not idleness, it is the key to wellness.',
            'Tomorrow is a fresh start with new possibilities.',
            'Peace comes from within - embrace the stillness.'
        ]
    
    # Get 2 random music files from the appropriate folder
    music_files = [
        {'file': f'{time_period}1.mp3', 'thumb': f'{time_period}1.jpg'},
        {'file': f'{time_period}2.mp3', 'thumb': f'{time_period}2.jpg'},
        {'file': f'{time_period}3.mp3', 'thumb': f'{time_period}3.jpg'},
        {'file': f'{time_period}4.mp3', 'thumb': f'{time_period}4.jpg'},
    ]
    
    # Select 2 random music files
    selected_music = random.sample(music_files, 2)
    
    # Add quotes and path to each music item
    for i, music in enumerate(selected_music):
        music['music_file'] = music['file']
        music['thumbnail'] = music['thumb']
        music['quote'] = quotes[i] if i < len(quotes) else quotes[0]
        music['title'] = f'{time_period.title()} Music {i+1}'
        music['music_path'] = f"music/{time_period}/{music['music_file']}"
    
    yoga_recommendations = [
        {
            'title': 'Scorpion Pose',
            'video': 'yogas_morning_time/scorpion-pose.mp4',
            'thumbnail': 'yoga_thumbnails/scorpion-pose.jpg',
            'description': 'Advanced pose for strength and balance.'
        },
        {
            'title': 'Meditation',
            'video': 'yogas_morning_time/meditation.mp4',
            'thumbnail': 'yoga_thumbnails/meditation.jpg',
            'description': 'Calm your mind and focus your breath.'
        },
        {
            'title': 'Child Pose',
            'video': 'yogas_morning_time/childpose.mp4',
            'thumbnail': 'yoga_thumbnails/childpose.jpg',
            'description': 'Gentle stretch for relaxation and rest.'
        },
        {
            'title': 'Balancing Stick',
            'video': 'yogas_morning_time/balancing_stick.mp4',
            'thumbnail': 'yoga_thumbnails/balancing_stick.jpg',
            'description': 'Improve balance and posture.'
        }
    ]
    return render_template(
        "index/health_tips.html",
        videos=videos,
        music_recommendations=selected_music,
        time_greeting=time_greeting,
        time_period=time_period,
        yoga_recommendations=yoga_recommendations
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

