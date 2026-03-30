import os
import cv2
import platform
import numpy as np
from PIL import Image
from pdf2image import convert_from_path

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"


if platform.system() == "Windows":
    POPPLER_PATH = r"C:\Users\Admin\Downloads\poppler-25.12.0\Library\bin"
else:
    POPPLER_PATH = None
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


def check_image_quality(image):

    height, width = image.shape[:2]

    if width < 800 or height < 600:
        print("Warning: Low resolution")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    brightness = np.mean(gray)

    if brightness < 60:
        print("Warning: Image too dark")
    elif brightness > 200:
        print("Warning: Image too bright")

    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

    if blur_score < 100:
        print("Warning: Image blurry")

    if width > height:
        print("Note: Image may be rotated")


def preprocess_image(image):

    # Convert PIL → OpenCV
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    check_image_quality(image)

    # --------- Resize (important for OCR) ---------
    image = cv2.resize(image, None, fx=1.3, fy=1.3, interpolation=cv2.INTER_CUBIC)

    return image


def process_file(file_path):

    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)
    ext = ext.lower()

    try:

        # ---------- PDF ----------
        if ext == ".pdf":

            pages = convert_from_path(
                file_path,
                dpi=150,
                poppler_path=POPPLER_PATH if POPPLER_PATH else None
            )

            saved_paths = []

            for i, page in enumerate(pages):

                processed = preprocess_image(page)

                save_path = os.path.join(PROCESSED_FOLDER, f"{name}_page{i+1}.jpg")

                cv2.imwrite(save_path, processed)

                saved_paths.append(save_path)

            return saved_paths   # 🔥 RETURN LIST

        # ---------- IMAGE ----------
        else:

            image = Image.open(file_path).convert("RGB")

            processed = preprocess_image(image)

            save_path = os.path.join(PROCESSED_FOLDER, f"{name}.jpg")

            cv2.imwrite(save_path, processed)

            return [save_path]   # 🔥 RETURN LIST

    except Exception as e:
        print("Error processing", filename, ":", str(e))
        return None
