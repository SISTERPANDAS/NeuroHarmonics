#!/usr/bin/env python
"""Add sample feedbacks for landing page display"""
from models import get_feedback_collection, get_users_collection, Feedback
from bson import ObjectId
from datetime import datetime, timedelta
import random

feedback_col = get_feedback_collection()
users_col = get_users_collection()

# Get first 5 users
users = list(users_col.find().limit(5))

if len(users) < 2:
    print("Not enough users to create sample feedbacks")
    exit(1)

# Sample feedback comments
comments = [
    "This app really helped me understand my emotions better!",
    "The personalized recommendations are amazing and very accurate.",
    "I love how the interface is so clean and easy to navigate.",
    "The music and yoga recommendations perfectly calmed my mind.",
    "Best wellness app I've tried so far. Highly recommend!",
    "The EEG analysis feature gave me great insights into my mental state.",
    "I've been using this for 2 weeks and already see positive changes.",
    "The community feedback section is so supportive and motivating."
]

# Create sample feedbacks
print("Adding sample feedbacks...")
for i, user in enumerate(users[:5]):
    if i == 0 or i == 1:
        continue  # Skip first two users as they already have feedbacks
    
    rating = random.randint(3, 5)
    comment = comments[random.randint(0, len(comments) - 1)]
    days_ago = random.randint(1, 20)
    created_at = datetime.utcnow() - timedelta(days=days_ago)
    
    feedback_col.insert_one({
        "user_id": user.get('_id'),
        "rating": rating,
        "comment": comment,
        "created_at": created_at
    })
    print(f"Added feedback from {user.get('username')} ({rating}⭐)")

# Count and display all feedbacks
all_feedbacks = list(feedback_col.find().sort("created_at", -1))
print(f'\nTotal feedbacks now in database: {len(all_feedbacks)}')
print('=' * 80)
print('\nAll feedbacks on landing page:')
for i, fb in enumerate(all_feedbacks, 1):
    user = users_col.find_one({'_id': fb.get('user_id')})
    user_name = user.get('username') if user else 'Unknown'
    rating = fb.get('rating')
    comment = fb.get('comment', '')[:50]
    print(f'{i}. {user_name} ({rating}⭐): {comment}...')
