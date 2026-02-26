from flask import Flask, render_template, redirect, session, request, jsonify
import os
from werkzeug.utils import secure_filename
from models import db, User
from auth_routes import auth
from admin_routes import admin

app = Flask(__name__)
app.secret_key = "super-secret-key"

db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'neuroharmonics.db')

@app.route('/update-profile', methods=['POST'])
def update_profile():
    """
    Update logged-in user's profile (username + avatar).
    Saves avatar in static/uploads/avatars.
    """

    # ✅ Check login
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    # ✅ SQLAlchemy safe fetch
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    try:
        # =========================
        # UPDATE USERNAME
        # =========================
        # Accept BOTH names for safety
        new_name = request.form.get('username')

        if new_name:
            new_name = new_name.strip()

            if len(new_name) < 2:
                return jsonify({'success': False, 'error': 'Name too short'}), 400

            user.username = new_name
            session['username'] = new_name

        # =========================
        # UPDATE AVATAR
        # =========================
        photo = request.files.get('avatar') or request.files.get('profile-photo')

        if photo and photo.filename:

            filename = secure_filename(photo.filename)
            ext = os.path.splitext(filename)[1].lower()

            # default extension fallback
            if not ext:
                ext = ".png"

            static_root = os.path.join(app.root_path, 'static')
            avatar_dir = os.path.join(static_root, 'uploads', 'avatars')
            os.makedirs(avatar_dir, exist_ok=True)

            # ✅ unique filename (prevents browser cache problem)
            stored_name = f"user_{user.id}_{int(datetime.utcnow().timestamp())}{ext}"
            avatar_fs_path = os.path.join(avatar_dir, stored_name)

            photo.save(avatar_fs_path)

            # relative path for url_for('static')
            avatar_rel_path = os.path.join('uploads', 'avatars', stored_name)

            user.avatar = avatar_rel_path
            session['avatar'] = avatar_rel_path

        # =========================
        # SAVE DATABASE
        # =========================
        db.session.commit()

        return jsonify({
            'success': True,
            'username': user.username,
            'avatar': user.avatar
        })

    except Exception as e:
        db.session.rollback()
        print("Update profile error:", e)
        return jsonify({'success': False, 'error': str(e)}), 500
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
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
    user = User.query.get(session["user_id"])
    if not user:
        return redirect("/logout")
    return render_template("dashboard/dashboard.html", user=user)

@app.route("/admin")
def admin_page():
    return render_template("admin/admin.html")

@app.route("/health-tips")
def health_tips():
    import random
    from datetime import datetime

    # --- Videos ---
    all_videos = [
        {
            'title': 'Create a New Morning Routine',
            'thumb': 'create_a_new_morning_routine.jpg',
            'video_path': 'videos/Create_a_new_morning_routine.mp4',
            'quote': 'Start your day with energy!',
            'tip': 'A positive morning routine boosts productivity.'
        },
        {
            'title': 'Body Movements',
            'thumb': 'body_movements.jpg',
            'video_path': 'videos/body_movements.mp4',
            'quote': 'Move for a healthy mind.',
            'tip': 'Simple stretches can improve your mood.'
        },
        {
            'title': 'Happy Activities',
            'thumb': 'happy_activities.jpg',
            'video_path': 'videos/happy_activities.mp4',
            'quote': 'Happiness is a habit.',
            'tip': 'Do something you love every day.'
        },
        {
            'title': 'Relaxed Time',
            'thumb': 'relaxed_time.jpg',
            'video_path': 'videos/relaxed_time.mp4',
            'quote': 'Rest is productive.',
            'tip': 'Take breaks to recharge your mind.'
        },
    ]
    videos = random.sample(all_videos, 4) if len(all_videos) >= 4 else all_videos

    # --- Yoga Recommendations ---
    yoga_recommendations = [
        {
            'title': 'Balancing Stick',
            'video': 'yogas_morning_time/balancing_stick.mp4',
            'thumbnail': 'yoga_thumbnails/balancing_stick.jpg',
            'description': 'Improve balance and focus.'
        },
        {
            'title': 'Child Pose',
            'video': 'yogas_morning_time/childpose.mp4',
            'thumbnail': 'yoga_thumbnails/childpose.jpg',
            'description': 'Relax and stretch your back.'
        },
        {
            'title': 'Meditation',
            'video': 'yogas_morning_time/meditation.mp4',
            'thumbnail': 'yoga_thumbnails/meditation.jpg',
            'description': 'Calm your mind and body.'
        },
        {
            'title': 'Scorpion Pose',
            'video': 'yogas_morning_time/scorpion-pose.mp4',
            'thumbnail': 'yoga_thumbnails/scorpion-pose.jpg',
            'description': 'Advanced pose for strength.'
        },
    ]

    # --- Music Recommendations ---
    current_hour = datetime.now().hour
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

    music_files = [
        {'music_path': f'music/{time_period}/{time_period}1.mp3', 'thumbnail': f'music_thumbnails/{time_period}/{time_period}1.jpg'},
        {'music_path': f'music/{time_period}/{time_period}2.mp3', 'thumbnail': f'music_thumbnails/{time_period}/{time_period}2.jpg'},
        {'music_path': f'music/{time_period}/{time_period}3.mp3', 'thumbnail': f'music_thumbnails/{time_period}/{time_period}3.jpg'},
        {'music_path': f'music/{time_period}/{time_period}4.mp3', 'thumbnail': f'music_thumbnails/{time_period}/{time_period}4.jpg'},
    ]
    selected_music = random.sample(music_files, 2)
    for i, music in enumerate(selected_music):
        music['quote'] = quotes[i] if i < len(quotes) else quotes[0]
        music['title'] = f'{time_period.title()} Music {i+1}'

    return render_template(
        "index/health_tips.html",
        videos=videos,
        music_recommendations=selected_music,
        yoga_recommendations=yoga_recommendations,
        time_greeting=time_greeting,
        time_period=time_period
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

