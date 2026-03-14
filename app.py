from flask import Flask, render_template, redirect, session, request, jsonify
import os
from datetime import datetime, timedelta
from models import User, CommunityMessage, SystemLog
from auth_routes import auth
from admin_routes import admin
import random
app = Flask(__name__, template_folder="templates")
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

        from models import get_users_collection
        if fullName:
            username_clean = fullName.strip()
            get_users_collection().update_one(
                {'_id': user_id},
                {'$set': {'username': username_clean}}
            )
            user = User.find_by_id(user_id)
            session['username'] = user.get('username')
            return jsonify({'success': True, 'username': user.get('username')})

        return jsonify({'success': False, 'error': 'No username provided'})
    except Exception as e:
        print('Update profile error:', e)
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/")
def home():
    # Always show landing page (do not redirect logged-in users to dashboard)
    # This ensures the URL lands on the home page as requested.
    
    # check database connectivity for display
    db_ok = False
    try:
        from models import client
        client.admin.command('ping')
        db_ok = True
    except Exception as e:
        print(f"DB connection check failed: {e}")
        db_ok = False

    # Fetch all feedbacks from database
    feedbacks_data = []
    if db_ok:
        try:
            from models import get_feedback_collection, get_users_collection
            feedback_col = get_feedback_collection()
            users_col = get_users_collection()
            
            # Get all feedbacks, no limit
            all_feedbacks = list(feedback_col.find().sort("created_at", -1))
            
            for fb in all_feedbacks:
                user_id = fb.get("user_id")  # Use user_id field from existing feedbacks
                if user_id:
                    # Find user by _id
                    user = users_col.find_one({"_id": user_id})
                    if user:
                        username = user.get("username", "Anonymous")
                        avatar = user.get("avatar", "")
                        
                        # Generate random avatar if not available
                        if not avatar:
                            import random
                            colors = ["FF6B6B", "4ECDC4", "45B7D1", "FFA07A", "98D8C8", "F38181", "AA96DA", "FCBAD3"]
                            random_color = random.choice(colors)
                            avatar = f"https://ui-avatars.com/api/?name={username}&background={random_color}&color=fff&size=100"
                        
                        feedbacks_data.append({
                            "feedback": fb,
                            "username": username,
                            "avatar": avatar
                        })
        except Exception as e:
            print(f"Error fetching feedbacks: {e}")
            # Fallback to demo feedbacks if database error
            feedbacks_data = [
                {
                    "feedback": {"rating": 5, "comment": "Amazing platform for mental wellness!"},
                    "username": "Demo User",
                    "avatar": "https://ui-avatars.com/api/?name=Demo+User&background=FF6B6B&color=fff&size=100"
                }
            ]

    return render_template("index/index.html", db_connected=db_ok, feedbacks=feedbacks_data)


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
        return redirect("/")
    
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

    # Also load feedback list so dashboard can display it live
    from models import get_feedback_collection, get_users_collection
    feedbacks_data = []
    try:
        feedback_col = get_feedback_collection()
        users_col = get_users_collection()
        all_feedbacks = list(feedback_col.find().sort("created_at", -1))
        for fb in all_feedbacks:
            user_info = None
            if fb.get("user_id"):
                try:
                    user_info = users_col.find_one({"_id": fb.get("user_id")})
                except Exception:
                    user_info = None

            username = (user_info.get("username") if user_info else (fb.get("username") or "Anonymous"))
            feedbacks_data.append({
                "rating": fb.get("rating", 0),
                "comment": fb.get("comment", ""),
                "created_at": fb.get("created_at"),
                "username": username
            })
    except Exception as e:
        print(f"Error loading feedback list: {e}")
        feedbacks_data = []

    # Pass messages and feedback list under variable names expected by template
    return render_template(
        "dashboard/dashboard.html",
        user=user,
        community_message=all_msgs,
        feedbacks=feedbacks_data
    )


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


@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    """Submit user feedback with rating and optional comment"""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    data = request.get_json() or {}
    rating = data.get("rating")
    comment = data.get("comment", "").strip()
    
    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"success": False, "error": "Invalid rating"}), 400
    
    try:
        from models import Feedback
        user_id = session["user_id"]
        feedback_id = Feedback.create(user_id=user_id, rating=rating, comment=comment)
        
        return jsonify({
            "success": True,
            "id": feedback_id,
            "message": "Feedback submitted successfully"
        })
    except Exception as e:
        print(f"Error submitting feedback: {e}")
        return jsonify({"success": False, "error": "Database error"}), 500


@app.route("/send-message", methods=["POST"])
def send_message():
    """Receive support contact messages and store in database"""
    data = request.get_json() if request.is_json else request.form.to_dict()
    # extract fields (name/email optional)
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    subject = data.get("subject", "").strip()
    message = data.get("message", "").strip()

    if not subject or not message:
        return jsonify({"success": False, "error": "Subject and message required"}), 400

    try:
        from models import ContactMessage
        user_id = session.get('user_id')
        msg_id = ContactMessage.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
            user_id=user_id
        )

        # Only persist message; do not attempt email sending
        return jsonify({"success": True, "id": msg_id})
    except Exception as e:
        print(f"Error saving support message: {e}")
        return jsonify({"success": False, "error": "Database error"}), 500


def send_confirmation_email(to_email, name, subject, user_message):
    """Send a confirmation email to the user who submitted the support message"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # Email configuration - using safe defaults (requires environment vars to actually send)
    SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
    FROM_EMAIL = os.environ.get("FROM_EMAIL", "mnop73359@gmail.com")
    
    # If no SMTP credentials configured, skip email send (non-critical)
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("Email not configured - skipping send")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"NeuroHarmonics: We received your message - {subject}"
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email
        
        # Plain text version
        text_content = f"""Dear {name},

Thank you for contacting NeuroHarmonics Support!

We have received your message:
Subject: {subject}
Message: {user_message}

Our team will review your message and get back to you within 24-48 hours.

Best regards,
NeuroHarmonics Support Team
"""
        
        # HTML version
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #9d4edd, #5a189a); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
        .message-box {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #9d4edd; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 NeuroHarmonics</h1>
            <p>Support Team</p>
        </div>
        <div class="content">
            <p>Dear <strong>{name}</strong>,</p>
            <p>Thank you for contacting NeuroHarmonics Support!</p>
            <div class="message-box">
                <p><strong>Subject:</strong> {subject}</p>
                <p><strong>Your Message:</strong></p>
                <p>{user_message}</p>
            </div>
            <p>Our team will review your message and get back to you within <strong>24-48 hours</strong>.</p>
            <p>Best regards,<br><strong>NeuroHarmonics Support Team</strong></p>
        </div>
        <div class="footer">
            <p>This is an automated response. Please do not reply to this email.</p>
            <p>© 2024 NeuroHarmonics. All rights reserved.</p>
        </div>
    </div>
</body>
</html>"""
        
        # Attach both versions
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        server.quit()
        
        print(f"Confirmation email sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise


def send_support_notification_email(user_name, user_email, subject, user_message):
    """Send notification email to support admin address(es)"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
    FROM_EMAIL = os.environ.get("FROM_EMAIL", "mnop73359@gmail.com")
    SUPPORT_EMAILS = os.environ.get("SUPPORT_EMAILS", "mnop73359@gmail.com")

    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("Email not configured - skipping support notification")
        return False

    recipient_list = [email.strip() for email in SUPPORT_EMAILS.split(",") if email.strip()]
    if not recipient_list:
        print("No support email recipients configured")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Support request received: {subject}"
        msg["From"] = FROM_EMAIL
        msg["To"] = ", ".join(recipient_list)

        text_content = f"""New support request from NeuroHarmonics:\n\nName: {user_name}\nEmail: {user_email}\nSubject: {subject}\nMessage: {user_message}\n"""

        html_content = f"""<!DOCTYPE html><html><body><h2>New Support Request</h2><p><strong>Name:</strong> {user_name}</p><p><strong>Email:</strong> {user_email}</p><p><strong>Subject:</strong> {subject}</p><p><strong>Message:</strong> {user_message}</p></body></html>"""

        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        msg.attach(part1)
        msg.attach(part2)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, recipient_list, msg.as_string())
        server.quit()

        print(f"Support notification sent to: {recipient_list}")
        return True

    except Exception as exc:
        print(f"Failed to send support notification: {exc}")
        raise


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
    # Ensure the main admin user exists on startup
    try:
        from models import User, get_users_collection
        from werkzeug.security import generate_password_hash
        
        # Configuration for the primary admin
        target_email = "ariyankapanda01@gmail.com"
        target_username = "admin2"
        
        admin_user = User.find_by_email(target_email)
        if not admin_user:
            print(f"--- Creating Default Admin ({target_username}) ---")
            User.create(
                username=target_username,
                email=target_email,
                password=generate_password_hash("admin456"),
                role="admin",
                status="active"
            )
        elif admin_user.get("role") != "admin":
            print(f"--- Promoting {target_username} to Admin ---")
            get_users_collection().update_one({"_id": admin_user["_id"]}, {"$set": {"role": "admin"}})
            
    except Exception as e:
        print(f"Startup Admin Check Failed: {e}")

    # Disable reloader on Windows to avoid WinError 10038 socket issues.
    app.run(debug=True, use_reloader=False, port=5001)
