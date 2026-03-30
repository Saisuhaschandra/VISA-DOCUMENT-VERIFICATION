import cv2
import numpy as np

def preprocess_face(image_path):
    img = cv2.imread(image_path)

    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    if len(faces) == 0:
        print("No face detected:", image_path)
        return None

    x, y, w, h = faces[0]

    # expand box
    margin = int(0.2 * w)
    x = max(0, x - margin)
    y = max(0, y - margin)
    w = w + 2 * margin
    h = h + 2 * margin

    face = gray[y:y+h, x:x+w]

    face = cv2.resize(face, (200, 200))

    return face


def compare_histogram(face1, face2):
    hist1 = cv2.calcHist([face1], [0], None, [256], [0,256])
    hist2 = cv2.calcHist([face2], [0], None, [256], [0,256])

    hist1 = cv2.normalize(hist1, hist1).flatten()
    hist2 = cv2.normalize(hist2, hist2).flatten()

    score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return score


from deepface import DeepFace

def match_faces(img1_path, img2_path):

    try:
        result = DeepFace.verify(
            img1_path,
            img2_path,
            model_name="SFace",   # 🔥 your model
            enforce_detection=False
        )

        print("\nDeepFace Comparison")
        print("Image1:", img1_path)
        print("Image2:", img2_path)
        print("Match:", result["verified"])
        print("Distance:", result["distance"])

        return result["verified"]

    except Exception as e:
        print("DeepFace Error:", str(e))
        return False

# ---------- FACE DETECTION ----------
def has_face(image_path):
    img = cv2.imread(image_path)

    if img is None:
        return False

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    return len(faces) > 0
