import os
import time

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# 🔥 suppress python warnings
import warnings
warnings.filterwarnings("ignore")

# 🔥 suppress tensorflow internal logging
import logging
logging.getLogger("tensorflow").setLevel(logging.FATAL)

# 🔥 extra keras suppression
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from flask import Flask, request, render_template, jsonify
import subprocess

def generate_requirements():
    if not os.path.exists("requirements.txt"):
        try:
            with open("requirements.txt", "w") as f:
                subprocess.run(["pip", "freeze"], stdout=f)
            print("✅ requirements.txt auto-created!")
        except Exception as e:
            print("❌ Failed to generate requirements:", e)

generate_requirements()
# 🔥 NEW IMPORTS
from face_verifier import match_faces, has_face
from doc_classifier import is_photo


# ---------- IMPORT ALL VALIDATORS ----------
from doc_classifier import (
    is_passport, is_visa, is_tenth, is_twelfth,
    is_degree, is_bank, is_sop, is_resume,
    is_itr, is_employment, is_offer_letter,
    is_salary_slip, is_gst, is_flight,
    is_hotel, is_insurance
)

from verifier import verify_documents
from preprocess import process_file
from ocr_reader import extract_text

app = Flask(__name__)

# ---------- FOLDERS ----------
UPLOAD_FOLDER = "uploads"
TEXT_FOLDER = "extracted_text"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEXT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------- TRACKING ----------
uploaded_docs = set()
uploaded_images = {}   # 🔥 store image paths

# ---------- HOME ----------
@app.route("/")
def index():
    return render_template("index.html")


# ---------- UPLOAD ----------
@app.route("/upload", methods=["POST"])
def upload():

    file = request.files.get("document")
    doc_type = request.form.get("type")

    if file is None:
        return jsonify({"status": "error", "message": "No document received"})

    if file.filename == "":
        return jsonify({"status": "error", "message": "No file selected"})

    if not doc_type:
        return jsonify({"status": "error", "message": "Document type missing"})

    # ---------- UNIQUE NAME ----------
    ext = os.path.splitext(file.filename)[1]
    filename = f"{doc_type}_{int(time.time())}{ext}"

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    print("File saved:", filepath)

    # 🔥 STORE IMAGE PATH
    uploaded_images[doc_type] = filepath

    # ---------- PREPROCESS ----------
    processed_paths = process_file(filepath)

    if processed_paths is None:
        return jsonify({"status": "error", "message": "Preprocessing failed"})

    # ---------- CLEAR OLD TEXT ----------
    txt_path = os.path.join(TEXT_FOLDER, f"{doc_type}.txt")
    if os.path.exists(txt_path):
        os.remove(txt_path)

    # ---------- OCR ----------
    full_text = ""

    for path in processed_paths:
        text = extract_text(path, doc_type)
        if text:
            full_text += text + "\n"

    # 🔥 FIX: allow empty OCR for photo
    if not full_text.strip() and doc_type != "photo":
        return jsonify({
            "status": "error",
            "message": "OCR failed"
        })

    # ---------- VALIDATION ----------
    valid = True
    message = "Valid document"

    if doc_type == "passport":
        valid = is_passport(full_text)
        message = "❌ Not a valid passport"

    elif doc_type == "visa":
        valid = is_visa(full_text)
        message = "❌ Not a valid visa"

    elif doc_type == "photo":
        valid = is_photo(full_text, filepath)   # 🔥 pass image path

    elif doc_type == "tenth":
        valid = is_tenth(full_text)
        message = "❌ Not a valid 10th"

    elif doc_type == "twelfth":
        valid = is_twelfth(full_text)
        message = "❌ Not a valid 12th"

    elif doc_type == "degree":
        valid = is_degree(full_text)
        message = "❌ Not a valid degree"

    elif doc_type == "bank":
        valid = is_bank(full_text)
        message = "❌ Not a valid bank statement"

    elif doc_type == "sop":
        valid = is_sop(full_text)
        message = "❌ Not a valid SOP"

    elif doc_type == "resume":
        valid = is_resume(full_text)
        message = "❌ Not a valid resume"

    # ---------- NEW DOCUMENT TYPES ----------
    elif doc_type == "itr":
        valid = is_itr(full_text)
        message = "❌ Not a valid ITR / Income Proof"

    elif doc_type == "employment":
        valid = is_employment(full_text)
        message = "❌ Not a valid Employment / Business Proof"

    elif doc_type == "offer_letter":
        valid = is_offer_letter(full_text)
        message = "❌ Not a valid Offer Letter"

    elif doc_type == "salary_slip":
        valid = is_salary_slip(full_text)
        message = "❌ Not a valid Salary Slip"

    elif doc_type == "gst":
        valid = is_gst(full_text)
        message = "❌ Not a valid GST Certificate"

    elif doc_type == "flight":
        valid = is_flight(full_text)
        message = "❌ Not a valid Flight Reservation"

    elif doc_type == "hotel":
        valid = is_hotel(full_text)
        message = "❌ Not a valid Hotel Booking"

    elif doc_type == "insurance":
        valid = is_insurance(full_text)
        message = "❌ Not a valid Travel Insurance"

    # ---------- RETURN ERROR ----------
    if not valid:
        return jsonify({
            "status": "error",
            "message": message
        })

    # ---------- STORE SUCCESS ----------
    uploaded_docs.add(doc_type)

    return jsonify({
        "status": "success",
        "message": "✔ Uploaded & Valid"
    })


# ---------- VERIFY ----------
@app.route("/verify", methods=["GET"])
def verify():



    # 🔥 FACE MATCHING
    # ---------- FACE MATCHING ----------
    photo_img = uploaded_images.get("photo")
    passport_img = uploaded_images.get("passport")
    visa_img = uploaded_images.get("visa")

    

    # ---------- PASSPORT CHECK ----------
    if passport_img:
        match_passport = match_faces(passport_img, photo_img)
        print("Passport match:", match_passport)

        if not match_passport:
            return jsonify({
                "status": "error",
                "result": "❌ Face mismatch: passport vs photo"
            })

    # ---------- VISA CHECK ----------
    if visa_img:
        match_visa = match_faces(visa_img, photo_img)
        print("Visa match:", match_visa)

        if not match_visa:
            return jsonify({
                "status": "error",
                "result": "❌ Face mismatch: visa vs photo"
            })
    # ---------- TEXT VERIFICATION ----------
    result = verify_documents()

    return jsonify({
        "status": "success",
        "result": result
    })


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

