import os
import time
import warnings
import logging

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

warnings.filterwarnings("ignore")
logging.getLogger("tensorflow").setLevel(logging.FATAL)

from flask import Flask, request, jsonify

#  IMPORTS 
from face_verifier import match_faces
from doc_classifier import (
    is_passport, is_visa, is_tenth, is_twelfth,
    is_degree, is_bank, is_sop, is_resume,
    is_itr, is_employment, is_offer_letter,
    is_salary_slip, is_gst, is_flight,
    is_hotel, is_insurance, is_photo
)

from verifier import verify_documents
from preprocess import process_file
from ocr_reader import extract_text

app = Flask(__name__)

#  FOLDERS 
UPLOAD_FOLDER = "uploads"
TEXT_FOLDER = "extracted_text"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEXT_FOLDER, exist_ok=True)

#  TRACKING 
uploaded_docs = set()
uploaded_images = {}

 
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Backend running"})


#  UPLOAD 
@app.route("/upload", methods=["POST"])
def upload():

    file = request.files.get("document")
    doc_type = request.form.get("type")

    if not file or file.filename == "":
        return jsonify({"status": "error", "message": "No file provided"})

    if not doc_type:
        return jsonify({"status": "error", "message": "Document type missing"})

    # Save file
    ext = os.path.splitext(file.filename)[1]
    filename = f"{doc_type}_{int(time.time())}{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    uploaded_images[doc_type] = filepath

    #  PREPROCESS 
    processed_paths = process_file(filepath)

    if not processed_paths:
        return jsonify({"status": "error", "message": "Preprocessing failed"})

    #  OCR 
    full_text = ""
    for path in processed_paths:
        text = extract_text(path, doc_type)
        if text:
            full_text += text + "\n"

    if not full_text.strip() and doc_type != "photo":
        return jsonify({"status": "error", "message": "OCR failed"})

    #  VALIDATION 
    valid = True
    message = "Valid document"

    if doc_type == "passport":
        valid = is_passport(full_text)
        message = "Invalid passport"

    elif doc_type == "visa":
        valid = is_visa(full_text)
        message = "Invalid visa"

    elif doc_type == "photo":
        valid = is_photo(full_text, filepath)

    elif doc_type == "tenth":
        valid = is_tenth(full_text)
        message = "Invalid 10th"

    elif doc_type == "twelfth":
        valid = is_twelfth(full_text)
        message = "Invalid 12th"

    elif doc_type == "degree":
        valid = is_degree(full_text)
        message = "Invalid degree"

    elif doc_type == "bank":
        valid = is_bank(full_text)
        message = "Invalid bank"

    elif doc_type == "sop":
        valid = is_sop(full_text)
        message = "Invalid SOP"

    elif doc_type == "resume":
        valid = is_resume(full_text)
        message = "Invalid resume"

    elif doc_type == "itr":
        valid = is_itr(full_text)

    elif doc_type == "employment":
        valid = is_employment(full_text)

    elif doc_type == "offer_letter":
        valid = is_offer_letter(full_text)

    elif doc_type == "salary_slip":
        valid = is_salary_slip(full_text)

    elif doc_type == "gst":
        valid = is_gst(full_text)

    elif doc_type == "flight":
        valid = is_flight(full_text)

    elif doc_type == "hotel":
        valid = is_hotel(full_text)

    elif doc_type == "insurance":
        valid = is_insurance(full_text)

    if not valid:
        return jsonify({"status": "error", "message": message})

    uploaded_docs.add(doc_type)

    return jsonify({"status": "success", "message": "Uploaded & Valid"})
#  VERIFY 
@app.route("/verify", methods=["GET"])
def verify():
    photo = uploaded_images.get("photo")
    passport = uploaded_images.get("passport")
    visa = uploaded_images.get("visa")
    # Face match
    if passport and photo:
        if not match_faces(passport, photo):
            return jsonify({"status": "error", "result": "Face mismatch (passport)"})
    if visa and photo:
        if not match_faces(visa, photo):
            return jsonify({"status": "error", "result": "Face mismatch (visa)"})
    # Text verification
    result = verify_documents()
    return jsonify({"status": "success", "result": result})
#  RUN 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
