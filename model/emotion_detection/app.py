# app.py: Flask backend for emotion detection web app
# Accepts image from frontend, runs model, returns detected emotion

from flask import Flask, request, jsonify, send_from_directory
import numpy as np
import cv2
import base64
from keras.models import model_from_json
from sklearn.metrics import accuracy_score

app = Flask(__name__, static_folder='static')

with open("emotiondetector.json", "r") as json_file:
    model_json = json_file.read()
model = model_from_json(model_json)
model.load_weights("emotiondetector.h5")

labels = {
    0: 'angry',
    1: 'disgust',
    2: 'fear',
    3: 'happy',
    4: 'neutral',
    5: 'sad',
    6: 'surprise'
}

# Calculate model accuracy (on test set if available)
model_accuracy = None
try:
    import os
    import numpy as np
    # If you have test images and labels, load and evaluate
    test_dir = os.path.join('images', 'test')
    X_test = []
    y_test = []
    for label_idx, label_name in labels.items():
        folder = os.path.join(test_dir, label_name)
        if os.path.exists(folder):
            for fname in os.listdir(folder):
                if fname.endswith('.png') or fname.endswith('.jpg'):
                    img_path = os.path.join(folder, fname)
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        img = cv2.resize(img, (48, 48))
                        X_test.append(img)
                        y_test.append(label_idx)
    if X_test and y_test:
        X_test = np.array(X_test).reshape(-1, 48, 48, 1) / 255.0
        y_test = np.array(y_test)
        preds = model.predict(X_test, verbose=0)
        pred_labels = np.argmax(preds, axis=1)
        model_accuracy = accuracy_score(y_test, pred_labels)
except Exception as e:
    model_accuracy = None

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    image_data = data['image']
    # Remove header ("data:image/png;base64,")
    image_data = image_data.split(',')[1]
    img_bytes = base64.b64decode(image_data)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return jsonify({'emotion': 'No face detected', 'accuracy': model_accuracy}), 200
    # Resize to 48x48 for model
    img = cv2.resize(img, (48, 48))
    img = img.reshape(1, 48, 48, 1) / 255.0
    pred = model.predict(img, verbose=0)
    emotion = labels[int(np.argmax(pred))]
    return jsonify({'emotion': emotion, 'accuracy': model_accuracy})

# To run: python app.py
# Visit http://localhost:5000/index.html
# Make sure index.html, script.js, style.css are in same folder


# Serve index.html at root
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# Serve static files (JS, CSS)
@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)
