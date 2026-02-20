from flask import Flask, render_template, redirect, session, request, url_for, flash, jsonify
from models import db, Feedback, ContactMessage, User, CommunityMessage, Admin # Added CommunityMessage
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

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")
    
    # 1. Get the current user object
    user = User.query.filter_by(username=session['username']).first()
    
    # 2. Fetch Community Messages (existing logic)
    messages = CommunityMessage.query.order_by(CommunityMessage.timestamp.asc()).limit(50).all()
    
    # 3. Fetch private inquiries sent by this user that have an admin reply
    # This assumes you added 'admin_reply' to your ContactMessage model
    personal_inquiries = ContactMessage.query.filter_by(user_id=user.id).all()
    
    return render_template("dashboard/dashboard.html", 
                           username=user.username, 
                           community_messages=messages,
                           inquiries=personal_inquiries) # Passing new data here

@app.route("/admin")
def admin_panel():
    if session.get("role") != "admin": # Security Check
        return redirect(url_for("admin_login_page"))
        
    users = User.query.all()
    users_count = User.query.count()
    messages = ContactMessage.query.filter_by(is_resolved=False).all()
    # analysis_count = EEGData.query.count() 

    return render_template("admin/admin.html", 
                           users=users, 
                           users_count=users_count,
                           messages=messages)

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

# 1. Route to serve the dedicated admin login page
@app.route("/admin-login-page")
def admin_login_page():
    return render_template("index/admin_login.html")

# 2. Route to process the credentials against the 'admins' table
from datetime import datetime

@app.route('/admin-login', methods=['POST'])
def admin_login_process():
    data = request.get_json()
    u_input = data.get('username').strip() # .strip() removes accidental spaces
    p_input = data.get('password').strip()

    # Query the 'admins' table
    admin_user = Admin.query.filter_by(username=u_input).first()

    if admin_user:
        # Debugging: These will appear in your VS Code / CMD terminal
        print(f"Comparing Input: [{p_input}] with DB: [{admin_user.password}]")
        
        if admin_user.password == p_input:
            admin_user.last_login = datetime.utcnow()
            db.session.commit()
            
            session['username'] = admin_user.username
            session['role'] = 'admin'
            return jsonify({"success": True, "redirect": url_for('admin_panel')})
        else:
            return jsonify({"success": False, "message": "Password mismatch"}), 401
    
    return jsonify({"success": False, "message": "Admin user not found"}), 401

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

@app.route('/admin-dashboard')
def admin_dashboard_view():
    # Security: Ensure only logged-in admins can see this
    if session.get('role') != 'admin':
        return redirect(url_for('login_page'))
        
    # For now, just render the template
    return render_template("admin/admin_login.html")

@app.route('/admin/reply-message', methods=['POST'])
def reply_message():
    if session.get('role') != 'admin':
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    msg_id = data.get('id')
    reply_text = data.get('reply')

    message = ContactMessage.query.get(msg_id)
    if message:
        message.admin_reply = reply_text
        message.is_resolved = True  # Mark as resolved so it clears from dashboard
        db.session.commit()
        return jsonify({"success": True})
    
    return jsonify({"success": False, "message": "Message not found"}), 404

if __name__ == "__main__":
    with app.app_context():
        db.create_all() # Ensures all tables (including Community) exist in Supabase
    app.run(debug=True)
