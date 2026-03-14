from models import get_users_collection
from werkzeug.security import generate_password_hash
import datetime

def import_admins():
    print("--- Importing Admins from CSV Data ---")
    
    # This connects to the database using your models.py connection
    users_col = get_users_collection()
    
    # The exact data provided
    admins_to_add = [
        {
            "name": "Ariyanka Panda",
            "email": "ariyankapanda01@gmail.com",
            "username": "admin2",
            "password": "admin456",
            "phone": "9998887071"
        },
        {
            "name": "Aratrika Panda",
            "email": "aratrikapanda10@gmail.com",
            "username": "admin3",
            "password": "admin789",
            "phone": "9998887072"
        },
        {
            "name": "Ashreya Awasthi",
            "email": "ashreyaawasthi000111@gmail.com",
            "username": "admin1",
            "password": "admin123",
            "phone": "9998887070"
        }
    ]

    for admin_data in admins_to_add:
        # Securely hash the plain text password
        hashed_pw = generate_password_hash(admin_data["password"])
        
        # Create the user document structure expected by the app
        user_doc = {
            "username": admin_data["username"],
            "email": admin_data["email"],
            "password": hashed_pw,
            "role": "admin",  # This ensures access to /admin
            "full_name": admin_data["name"],
            "phone": admin_data["phone"],
            "status": "active",
            "created_at": datetime.datetime.utcnow()
        }

        # Update if exists, Insert if new
        existing = users_col.find_one({"email": admin_data["email"]})
        if existing:
            print(f"Updating existing admin: {admin_data['name']}")
            users_col.update_one(
                {"_id": existing["_id"]},
                {"$set": user_doc}
            )
        else:
            print(f"Creating new admin: {admin_data['name']}")
            users_col.insert_one(user_doc)

    print("\n--- Success! ---")
    print("You can now log in to the dashboard with these credentials.")

if __name__ == "__main__":
    import_admins()