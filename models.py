"""MongoDB Database Models for NeuroHarmonics"""
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
import os

# MongoDB Connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://neuroadmin:Strongpassword123@cluster0.phmuefa.mongodb.net/?appName=Cluster0")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Test connection
    client.admin.command('ping')
    print("[+] MongoDB connection successful")
except Exception as e:
    print(f"[-] MongoDB connection failed: {e}")
    raise

db = client.neuroharmonics

# Collections
def get_users_collection():
    return db.users

def get_recommendations_collection():
    return db.recommendations

def get_system_logs_collection():
    return db.system_logs

def get_feedback_collection():
    return db.feedback

def get_contact_messages_collection():
    return db.contact_messages

def get_community_message_collection():
    return db.community_message

def get_emotion_logs_collection():
    return db.emotion_logs


class User:
    """User model for MongoDB"""
    
    @staticmethod
    def create(username, email, password, role="user", status="active", avatar=None):
        """Create a new user"""
        user_data = {
            "username": username,
            "email": email,
            "password": password,
            "role": role,
            "status": status,
            "created_at": datetime.utcnow(),
            "avatar": avatar or ""
        }
        result = get_users_collection().insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        user = get_users_collection().find_one({"email": email})
        return user
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        user = get_users_collection().find_one({"_id": user_id})
        return user
    
    @staticmethod
    def find_by_username(username):
        """Find user by username"""
        user = get_users_collection().find_one({"username": username})
        return user
    
    @staticmethod
    def update_status(user_id, status):
        """Update user status"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        result = get_users_collection().update_one(
            {"_id": user_id},
            {"$set": {"status": status}}
        )
        return result.modified_count > 0
    
    @staticmethod
    def get_all():
        """Get all users"""
        return list(get_users_collection().find())
    
    @staticmethod
    def count():
        """Count total users"""
        return get_users_collection().count_documents({})


class Recommendation:
    """Recommendation model for MongoDB"""
    
    @staticmethod
    def create(emotion, content):
        """Create a new recommendation"""
        rec_data = {
            "emotion": emotion,
            "content": content,
            "created_at": datetime.utcnow()
        }
        result = get_recommendations_collection().insert_one(rec_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_all():
        """Get all recommendations"""
        return list(get_recommendations_collection().find())


class SystemLog:
    """System log model for MongoDB"""
    
    @staticmethod
    def create(message, level="INFO"):
        """Create a new system log"""
        log_data = {
            "message": message,
            "level": level,
            "timestamp": datetime.utcnow()
        }
        result = get_system_logs_collection().insert_one(log_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_recent(limit=50):
        """Get recent logs"""
        return list(get_system_logs_collection().find().sort("timestamp", -1).limit(limit))
    
    @staticmethod
    def count_by_level(level):
        """Count logs by level"""
        return get_system_logs_collection().count_documents({"level": level})


class Feedback:
    """Feedback model for MongoDB"""
    
    @staticmethod
    def create(user_id, rating, comment=None):
        """Create new feedback"""
        feedback_data = {
            "_id": ObjectId(user_id) if isinstance(user_id, str) else user_id,
            "rating": rating,
            "comment": comment,
            "created_at": datetime.utcnow()
        }
        result = get_feedback_collection().insert_one(feedback_data)
        return str(result.inserted_id)


class ContactMessage:
    """Contact message model for MongoDB"""
    
    @staticmethod
    def create(name, email, subject, message, user_id=None):
        """Create a new contact message"""
        msg_data = {
            "user_id": ObjectId(user_id) if isinstance(user_id, str) else user_id,
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
            "is_resolved": False,
            "admin_reply": None,
            "timestamp": datetime.utcnow()
        }
        result = get_contact_messages_collection().insert_one(msg_data)
        return str(result.inserted_id)


class CommunityMessage:
    """Community message model for MongoDB"""
    
    @staticmethod
    def create(username, content):
        """Create a new community message"""
        msg_data = {
            "username": username,
            "content": content,
            "timestamp": datetime.utcnow()
        }
        result = get_community_message_collection().insert_one(msg_data)
        return str(result.inserted_id)


class EmotionLog:
    """Emotion log model for MongoDB"""
    
    @staticmethod
    def create(user_id, emotion):
        """Create a new emotion log"""
        log_data = {
            "user_id": ObjectId(user_id) if isinstance(user_id, str) else user_id,
            "emotion": emotion,
            "timestamp": datetime.utcnow()
        }
        result = get_emotion_logs_collection().insert_one(log_data)
        return str(result.inserted_id)
