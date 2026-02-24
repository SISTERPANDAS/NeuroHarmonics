import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from keras.models import model_from_json
from tkinterdnd2 import DND_FILES, TkinterDnD


# =========================
# LOAD MODEL
# =========================
def load_emotion_model():

    with open("emotiondetector.json", "r") as json_file:
        model_json = json_file.read()

    model = model_from_json(model_json)
    model.load_weights("emotiondetector.h5")

    print("Emotion model loaded successfully")
    return model


# =========================
# FEATURE EXTRACTION
# =========================
def extract_features(image):
    feature = np.array(image)
    feature = feature.reshape(1, 48, 48, 1)
    return feature / 255.0


# =========================
# PREDICT EMOTION
# =========================
def predict_emotion(model, face_img):

    labels = {
        0: 'angry',
        1: 'disgust',
        2: 'fear',
        3: 'happy',
        4: 'neutral',
        5: 'sad',
        6: 'surprise'
    }

    img = extract_features(face_img)
    pred = model.predict(img, verbose=0)
    return labels[int(np.argmax(pred))]


# =========================
# MAIN APPLICATION
# =========================
class EmotionApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Emotion Detection Application")
        self.root.geometry("1000x700")

        self.model = load_emotion_model()

        haar = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(haar)

        self.cap = None

        # MAIN CONTAINER
        self.container = tk.Frame(root)
        self.container.pack(fill="both", expand=True)

        self.show_home()

    # =========================
    # CLEAR SCREEN
    # =========================
    def clear(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # =========================
    # HOME SCREEN
    # =========================
    def show_home(self):

        self.clear()

        title = tk.Label(self.container,
                         text="Emotion Detection Interface",
                         font=("Arial", 24))
        title.pack(pady=40)

        tk.Button(self.container,
                  text="📷 Capture (Live Camera)",
                  font=("Arial", 16),
                  width=25,
                  command=self.open_camera_mode).pack(pady=20)

        tk.Button(self.container,
                  text="🖼 Browse / Drag & Drop",
                  font=("Arial", 16),
                  width=25,
                  command=self.open_browse_mode).pack(pady=20)

        tk.Button(self.container,
                  text="Exit",
                  font=("Arial", 14),
                  command=self.root.destroy).pack(pady=40)

    # =========================
    # CAMERA MODE
    # =========================
    def open_camera_mode(self):

        self.clear()

        self.cap = cv2.VideoCapture(0)

        self.display = tk.Label(self.container)
        self.display.pack(pady=10)

        self.result_label = tk.Label(self.container,
                                     text="Emotion: ---",
                                     font=("Arial", 18))
        self.result_label.pack(pady=10)

        btn_frame = tk.Frame(self.container)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame,
                  text="Capture",
                  font=("Arial", 14),
                  command=self.capture_emotion).grid(row=0, column=0, padx=10)

        tk.Button(btn_frame,
                  text="Back",
                  font=("Arial", 14),
                  command=self.back_to_home).grid(row=0, column=1, padx=10)

        tk.Button(btn_frame,
                  text="Exit",
                  font=("Arial", 14),
                  command=self.root.destroy).grid(row=0, column=2, padx=10)

        self.update_camera()

    def update_camera(self):

        if self.cap is None:
            return

        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame.copy()

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            img = img.resize((900, 500))  # BIG CAMERA VIEW
            imgtk = ImageTk.PhotoImage(image=img)

            self.display.imgtk = imgtk
            self.display.configure(image=imgtk)

        self.root.after(10, self.update_camera)

    def capture_emotion(self):

        frame = self.current_frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        emotion_text = "No face detected"

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (48, 48))
            emotion_text = predict_emotion(self.model, face)
            break

        self.result_label.config(text=f"Emotion: {emotion_text}")

    # =========================
    # BROWSE MODE
    # =========================
    def open_browse_mode(self):

        self.clear()

        self.display = tk.Label(self.container,
                                text="Drag & Drop Image Here",
                                bg="black",
                                fg="white",
                                width=80,
                                height=25)
        self.display.pack(pady=20)

        self.display.drop_target_register(DND_FILES)
        self.display.dnd_bind('<<Drop>>', self.drop_image)

        self.result_label = tk.Label(self.container,
                                     text="Emotion: ---",
                                     font=("Arial", 18))
        self.result_label.pack(pady=10)

        btn_frame = tk.Frame(self.container)
        btn_frame.pack()

        tk.Button(btn_frame,
                  text="Browse Image",
                  font=("Arial", 14),
                  command=self.browse_image).grid(row=0, column=0, padx=10)

        tk.Button(btn_frame,
                  text="Back",
                  font=("Arial", 14),
                  command=self.back_to_home).grid(row=0, column=1, padx=10)

        tk.Button(btn_frame,
                  text="Exit",
                  font=("Arial", 14),
                  command=self.root.destroy).grid(row=0, column=2, padx=10)

    def browse_image(self):

        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )

        if file_path:
            frame = cv2.imread(file_path)
            self.show_image(frame)
            self.detect_from_frame(frame)

    def drop_image(self, event):

        file_path = event.data.strip("{}")
        frame = cv2.imread(file_path)
        self.show_image(frame)
        self.detect_from_frame(frame)

    def show_image(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        img = img.resize((900, 500))
        imgtk = ImageTk.PhotoImage(image=img)

        self.display.imgtk = imgtk
        self.display.configure(image=imgtk)

    def detect_from_frame(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        emotion_text = "No face detected"

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (48, 48))
            emotion_text = predict_emotion(self.model, face)
            break

        self.result_label.config(text=f"Emotion: {emotion_text}")

    # =========================
    # BACK BUTTON
    # =========================
    def back_to_home(self):

        if self.cap is not None:
            self.cap.release()
            self.cap = None

        self.show_home()


# =========================
# RUN APP
# =========================
if __name__ == "__main__":

    root = TkinterDnD.Tk()
    app = EmotionApp(root)
    root.mainloop()