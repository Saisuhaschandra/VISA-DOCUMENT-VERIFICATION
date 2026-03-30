import os
import time

# Disable MKLDNN issues for cmd 
#os.environ["FLAGS_use_mkldnn"] = "0"
#os.environ["FLAGS_enable_pir_api"] = "0"

from flask import Flask, request, render_template, jsonify

from doc_classifier import (
    is_passport, is_visa, is_tenth, is_twelfth,
    is_degree, is_bank, is_sop, is_resume
)

from verifier import verify_documents
from preprocess import process_file
from ocr_reader import extract_text


#  GLOBAL STORAGE 
uploaded_images = {}
extracted_texts = {}
uploaded_docs = set()

app = Flask(__name__)

#  FOLDERS 
UPLOAD_FOLDER = "uploads"
TEXT_FOLDER = "extracted_text"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEXT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


#  HOME 
@app.route("/")
def index():
    return render_template("index.html")


#  UPLOAD 
@app.route("/upload", methods=["POST"])
def upload():

    file = request.files.get("document")
    doc_type = request.form.get("type")

    if not file or file.filename == "":
        return jsonify({"status": "error", "message": "No file selected"})

    if not doc_type:
        return jsonify({"status": "error", "message": "Document type missing"})

    #  SAVE FILE 
    ext = os.path.splitext(file.filename)[1]
    filename = f"{doc_type}_{int(time.time())}{ext}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    print("\nUploaded:", filepath)

    #  PREPROCESS 
    processed_paths = process_file(filepath)

    #  STORE IMAGE FOR FACE MATCH 
    if processed_paths and len(processed_paths) > 0:
        uploaded_images[doc_type] = processed_paths[0]
    else:
        uploaded_images[doc_type] = filepath

    print("Stored image:", uploaded_images[doc_type])

    #  PHOTO (NO OCR NEEDED) 
    if doc_type == "photo":
        extracted_texts[doc_type] = ""
        uploaded_docs.add(doc_type)

        return jsonify({
            "status": "success",
            "message": "✔ Photo uploaded"
        })

    #  OCR 
    full_text = ""

    for path in processed_paths:
        text = extract_text(path, doc_type)
        if text:
            full_text += text + "\n"

    if not full_text.strip():
        return jsonify({
            "status": "error",
            "message": "OCR failed"
        })

    extracted_texts[doc_type] = full_text

    #  VALIDATION 
    valid = True

    if doc_type == "passport":
        valid = is_passport(full_text)

    elif doc_type == "visa":
        valid = is_visa(full_text)

    elif doc_type == "tenth":
        valid = is_tenth(full_text)

    elif doc_type == "twelfth":
        valid = is_twelfth(full_text)

    elif doc_type == "degree":
        valid = is_degree(full_text)

    elif doc_type == "bank":
        valid = is_bank(full_text)

    elif doc_type == "sop":
        valid = is_sop(full_text)

    elif doc_type == "resume":
        valid = is_resume(full_text)

    if not valid:
        return jsonify({
            "status": "error",
            "message": f"❌ Invalid {doc_type}"
        })

    #  STORE 
    uploaded_docs.add(doc_type)

    return jsonify({
        "status": "success",
        "message": "✔ Uploaded & Valid"
    })


#  VERIFY 
@app.route("/verify", methods=["GET"])
def verify():

    if len(uploaded_docs) == 0:
        return jsonify({
            "status": "error",
            "result": "❌ No documents uploaded"
        })

    result = verify_documents(uploaded_images, extracted_texts)

    return jsonify({
        "status": "success",
        "result": result
    })

#  RUN 
if __name__ == "__main__":
    app.run(debug=True)
