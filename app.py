from flask import Flask, render_template, redirect, session, request, jsonify
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from models import User, CommunityMessage, SystemLog
from auth_routes import auth
from admin_routes import admin
import random

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "super-secret-key")
app.permanent_session_lifetime = timedelta(days=30)

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(admin)


@app.route('/update-profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    try:
        from bson import ObjectId
        user_id = ObjectId(session['user_id']) if isinstance(session['user_id'], str) else session['user_id']
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        fullName = request.form.get('fullName') or request.form.get('username')
        photo = request.files.get('photo')

        if fullName:
            # Update username in MongoDB
            from models import get_users_collection
            get_users_collection().update_one(
                {"_id": user_id},
                {"$set": {"username": fullName.strip()}}
            )

        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            ext = os.path.splitext(filename)[1].lower() or ".png"
            static_root = os.path.join(app.root_path, 'static')
            avatar_dir = os.path.join(static_root, 'uploads', 'avatars')
            os.makedirs(avatar_dir, exist_ok=True)
            stored_name = f"user_{user['_id']}_{int(datetime.utcnow().timestamp())}{ext}"
            avatar_fs_path = os.path.join(avatar_dir, stored_name)
            photo.save(avatar_fs_path)
            avatar_rel_path = os.path.join('uploads', 'avatars', stored_name)
            
            # Update avatar in MongoDB
            from models import get_users_collection
            get_users_collection().update_one(
                {"_id": user_id},
                {"$set": {"avatar": avatar_rel_path}}
            )
            session['avatar'] = avatar_rel_path

        return jsonify({'success': True, 'username': fullName, 'avatar': user.get('avatar', '')})
    except Exception as e:
        print("Update profile error:", e)
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/")
def home():
    # if user already logged in, skip the landing page
    if "user_id" in session:
        return redirect("/dashboard")

    # check database connectivity for display
    db_ok = False
    try:
        from models import client
        client.admin.command('ping')
        db_ok = True
    except Exception as e:
        print(f"DB connection check failed: {e}")
        db_ok = False

    return render_template("index/index.html", db_connected=db_ok)


@app.route("/login", methods=["GET"])
def login_page():
    if "user_id" in session:
        return redirect("/dashboard")
    return render_template("index/login.html")


@app.route("/register", methods=["GET"])
def register_page():
    if "user_id" in session:
        return redirect("/dashboard")
    return render_template("index/login.html")


@app.route("/health-tips")
def health_tips():
    """Render the mental wellness tips page with three time‑of‑day frames.

    Each of the following frames appears on the page regardless of the
    current hour:

      * **Morning** – 4 AM through 12 PM
      * **Afternoon** – 12 PM through 5 PM
      * **Evening** – 5 PM through 4 AM

    The music directories in ``static/music`` are expected to be organised as
    ``morning``, ``evening`` (used for the afternoon frame) and ``night`` (for
    the evening frame); their thumbnails live under the corresponding
    subfolder of ``static/music_thumbnails``.  Four random animation videos
    from ``static/videos`` are chosen each visit and shown under the frames.
    """
    import random

    static_root = app.static_folder

    periods = [
        {
            "key": "morning",
            "label": "Morning (4 AM – 12 PM)",
            "music_folder": "music/morning",
            "thumb_folder": "music_thumbnails/morning",
        },
        {
            "key": "afternoon",
            "label": "Afternoon (12 PM – 5 PM)",
            "music_folder": "music/evening",
            "thumb_folder": "music_thumbnails/evening",
        },
        {
            "key": "evening",
            "label": "Evening (5 PM – 4 AM)",
            "music_folder": "music/night",
            "thumb_folder": "music_thumbnails/night",
        },
    ]

    # choose a single period based on local system time
    from datetime import datetime
    # allow forcing the period for local testing via query param
    forced = request.args.get('force_period')
    if forced in ('morning', 'afternoon', 'evening'):
        sel_key = forced
    else:
        now = datetime.now()
        hour = now.hour
        if hour >= 4 and hour < 12:
            sel_key = "morning"
        elif hour >= 12 and hour < 20:
            sel_key = "afternoon"
        else:
            sel_key = "evening"

    selected = next((p for p in periods if p["key"] == sel_key), periods[0])
    recs = []
    dirpath = os.path.join(static_root, selected["music_folder"])
    try:
        files = [f for f in os.listdir(dirpath) if f.lower().endswith(".mp3")]
    except Exception:
        files = []
    random.shuffle(files)
    for fname in files[:3]:
        base = os.path.splitext(fname)[0]
        thumb_path = os.path.join(static_root, selected["thumb_folder"], f"{base}.jpg")
        thumb_rel = f"{selected['thumb_folder']}/{base}.jpg" if os.path.exists(thumb_path) else ""
        recs.append({
            "music_path": f"{selected['music_folder']}/{fname}",
            "thumbnail": thumb_rel,
            "title": base.replace("_", " ").title(),
            "quote": "Relax with some music",
        })

    periods_data = [{"key": selected["key"], "label": selected["label"], "music_recommendations": recs}]

    # tip videos: pick four random clips
    videos = []
    vdir = os.path.join(static_root, "videos")
    try:
        all_videos = [f for f in os.listdir(vdir) if f.lower().endswith(".mp4")]
    except Exception:
        all_videos = []
    random.shuffle(all_videos)
    for fname in all_videos[:4]:
        base = os.path.splitext(fname)[0]
        thumb_name = f"{base}.jpg"
        thumb_path = os.path.join(static_root, "dashboard", "video_thumbs", thumb_name)
        thumb_rel = f"dashboard/video_thumbs/{thumb_name}" if os.path.exists(thumb_path) else ""
        videos.append({
            "thumb": thumb_rel,
            "title": base.replace("_", " ").title(),
            "quote": "",
            "tip": "",
            "video_path": f"videos/{fname}",
        })

    # yoga suggestions unchanged
    yoga_recommendations = []
    yoga_dir = os.path.join(static_root, "yogas_morning_time")
    thumb_files = {}
    try:
        for f in os.listdir(os.path.join(static_root, "yoga_thumbnails")):
            key = os.path.splitext(f)[0].lower().replace("-", "").replace("_", "")
            thumb_files[key] = f
    except Exception:
        pass
    try:
        for fname in os.listdir(yoga_dir):
            if not fname.lower().endswith(".mp4"):
                continue
            base = os.path.splitext(fname)[0]
            key = base.lower().replace("-", "").replace("_", "")
            thumb = thumb_files.get(key, "")
            yoga_recommendations.append({
                "video": f"yogas_morning_time/{fname}",
                "thumbnail": f"yoga_thumbnails/{thumb}" if thumb else "",
                "title": base.replace("-", " ").title(),
                "description": "A relaxing yoga pose",
            })
    except Exception:
        yoga_recommendations = []

    return render_template(
        "index/health_tips.html",
        periods=periods_data,
        videos=videos,
        yoga_recommendations=yoga_recommendations,
    )


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    
    from bson import ObjectId
    user_id = ObjectId(session["user_id"]) if isinstance(session["user_id"], str) else session["user_id"]
    user = User.find_by_id(user_id)
    if not user:
        return redirect("/logout")

    # Load all community messages (do not delete old messages) and pass to template
    from models import get_community_message_collection
    try:
        all_msgs = list(get_community_message_collection().find().sort("timestamp", 1))
    except Exception as e:
        print(f"Error loading community messages: {e}")
        all_msgs = []

    # Normalize timestamps: ensure datetime objects for template `.strftime` calls
    def _parse_dt(v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # Try ISO format first, then common datetime formats
            try:
                return datetime.fromisoformat(v)
            except Exception:
                pass
            for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(v, fmt)
                except Exception:
                    pass
        return None

    for m in all_msgs:
        try:
            ts = m.get("timestamp")
            parsed = _parse_dt(ts)
            if parsed:
                m["timestamp"] = parsed
            else:
                # Fallback to current time so template rendering won't fail
                m["timestamp"] = datetime.utcnow()
        except Exception:
            m["timestamp"] = datetime.utcnow()

    # Pass messages under the variable name expected by the template
    return render_template("dashboard/dashboard.html", user=user, community_message=all_msgs)


@app.route("/admin")
def admin_page():
    return render_template("admin/admin.html")


@app.route("/status")
def status():
    """Return simple JSON indicating whether the database is reachable."""
    db_ok = False
    try:
        from models import client
        client.admin.command('ping')
        db_ok = True
    except Exception:
        db_ok = False
    return jsonify({"db_connected": db_ok, "user": session.get("user_id")})


@app.route("/logout")
def logout():
    """Log the current user out and redirect to the homepage.

    This clears the Flask session and marks the user inactive in the database.
    JavaScript may call this URL (e.g. via window.location) to perform a logout.
    """
    user_id = session.get("user_id")
    if user_id:
        try:
            User.update_status(user_id, "offline")
        except Exception as e:
            print(f"Error updating user status: {e}")
    session.clear()
    return redirect("/")


@app.route("/post-community", methods=["POST"])
def post_community():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    data = request.get_json() or {}
    msg = data.get("message", "").strip()
    if not msg:
        return jsonify({"success": False, "error": "Empty message"}), 400
    
    from bson import ObjectId
    user_id = ObjectId(session["user_id"]) if isinstance(session["user_id"], str) else session["user_id"]
    user = User.find_by_id(user_id)
    username = user['username'] if user and user.get('username') else (user['email'].split('@')[0] if user and user.get('email') else "User")
    
    try:
        msg_id = CommunityMessage.create(username=username, content=msg)
        return jsonify({
            "success": True,
            "id": msg_id,
            "username": username,
            "content": msg,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        print(f"Error posting community message: {e}")
        return jsonify({"success": False, "error": "Database error"}), 500


@app.route("/launch-game", methods=["POST"])
def launch_game():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    data = request.get_json() or {}
    game = data.get("game", "").strip().lower()
    if game == "space_invaders":
        try:
            import subprocess, shutil
            project_root = os.path.dirname(__file__)
            venv_script = os.path.join(project_root, "backend", "venv", "Scripts", "space-invaders.exe")
            candidate = None
            if os.path.exists(venv_script):
                candidate = venv_script
            else:
                which_path = shutil.which("space-invaders")
                if which_path:
                    candidate = which_path
            if not candidate:
                return jsonify({"success": False, "error": "Space Invaders executable not found."}), 400
            CREATE_NEW_CONSOLE = 0x00000010
            try:
                subprocess.Popen([candidate], creationflags=CREATE_NEW_CONSOLE)
            except TypeError:
                subprocess.Popen([candidate])
            return jsonify({"success": True})
        except Exception as e:
            print("Launch game error:", e)
            return jsonify({"success": False, "error": str(e)}), 500
    return jsonify({"success": False, "error": "Unknown game"}), 400


if __name__ == "__main__":
    app.run(debug=True)

