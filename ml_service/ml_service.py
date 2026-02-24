from fastapi import FastAPI, File, UploadFile
import random

app = FastAPI()

@app.post("/analyze-face")
async def analyze_face(image: UploadFile = File(...)):

    emotions = ["happy","neutral","calm","focused"]

    return {
        "dominantEmotion": random.choice(emotions),
        "emotionDistribution":{
            "happy":0.3,
            "neutral":0.3,
            "calm":0.4
        },
        "confidenceScore":0.86,
        "faceLandmarks":[]
    }