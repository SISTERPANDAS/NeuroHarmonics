from flask import Blueprint, request, jsonify, session
import requests
from models import db, EmotionLog
from datetime import datetime

face = Blueprint("face", __name__)

ML_SERVICE_URL = "http://localhost:8000/analyze-face"

@face.route("/api/face/analyze", methods=["POST"])
def analyze_face():

    if "username" not in session:
        return jsonify({"error":"Unauthorized"}),401

    image = request.files.get("image")
    if not image:
        return jsonify({"error":"No image provided"}),400

    files = {"image": (image.filename, image.stream, image.mimetype)}

    res = requests.post(ML_SERVICE_URL, files=files)

    data = res.json()

    log = EmotionLog(
        user_id=session["user_id"],
        dominant_emotion=data["dominantEmotion"],
        emotion_distribution=data["emotionDistribution"],
        confidence_score=data["confidenceScore"],
        created_at=datetime.utcnow()
    )

    db.session.add(log)
    db.session.commit()

    return jsonify(data)