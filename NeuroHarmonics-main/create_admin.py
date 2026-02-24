"""
One-time script to create a sample admin user for NeuroHarmonics.
Run: python create_admin.py
Then log in at /login with the credentials below.
"""
import os
from app import app
from models import db, User
from werkzeug.security import generate_password_hash

# Sample admin credentials (change in production!)
ADMIN_EMAIL = "admin@neuroharmonics.com"
ADMIN_PASSWORD = "Admin@123"
ADMIN_USERNAME = "Admin"

with app.app_context():
    # Ensure new columns exist (for existing SQLite DBs created before model update)
    try:
        db.session.execute(db.text("ALTER TABLE user ADD COLUMN is_active BOOLEAN DEFAULT 1"))
        db.session.commit()
    except Exception:
        db.session.rollback()
    try:
        db.session.execute(db.text("ALTER TABLE user ADD COLUMN last_login_at DATETIME"))
        db.session.commit()
    except Exception:
        db.session.rollback()

    existing = User.query.filter_by(email=ADMIN_EMAIL).first()
    if existing:
        existing.role = "admin"
        existing.username = ADMIN_USERNAME
        existing.password = generate_password_hash(ADMIN_PASSWORD)
        existing.is_active = True
        db.session.commit()
        print("Updated existing user to admin.")
    else:
        user = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=generate_password_hash(ADMIN_PASSWORD),
            role="admin",
            status="active",
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()
        print("Admin user created.")
    print("\n--- Sample admin login ---")
    print("  URL:      http://127.0.0.1:5000/login")
    print("  Email:    ", ADMIN_EMAIL)
    print("  Password: ", ADMIN_PASSWORD)
    print("  Then go to: http://127.0.0.1:5000/admin")
    print("----------------------------\n")
