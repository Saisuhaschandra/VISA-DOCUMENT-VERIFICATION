import easyocr
import os
import platform
from pdf2image import convert_from_path

#  POPPLER SETUP 
if platform.system() == "Windows":
    POPPLER_PATH = r"C:\Users\Admin\Downloads\poppler-25.12.0\Library\bin"
else:
    POPPLER_PATH = None

reader = easyocr.Reader(['en'], gpu=False)

TEXT_FOLDER = "extracted_text"
os.makedirs(TEXT_FOLDER, exist_ok=True)

def pdf_to_images(file_path):
    if POPPLER_PATH:
        return convert_from_path(file_path, poppler_path=POPPLER_PATH)
    else:
        return convert_from_path(file_path)

def extract_text(file_path, doc_type):
    text = ""

    if file_path.lower().endswith(".pdf"):
        images = pdf_to_images(file_path)
        for img in images:
            results = reader.readtext(img, detail=0)
            for txt in results:
                text += txt + "\n"
    else:
        results = reader.readtext(file_path, detail=0)
        for txt in results:
            text += txt + "\n"

    save_path = os.path.join(TEXT_FOLDER, f"{doc_type}.txt")

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(text)

    return text
