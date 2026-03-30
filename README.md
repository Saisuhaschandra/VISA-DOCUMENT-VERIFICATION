# VISA-DOCUMENT-VERIFICATION AI


A backend-based system to verify multiple user documents using **OCR, MRZ parsing, and face recognition**.
It ensures that all uploaded documents belong to the same person.

---

## 🚀 Features

* Upload multiple documents (Passport, Visa, Photo, 10th, 12th, Degree)
* Extract text using OCR (EasyOCR)
* Detect document type automatically
* Extract passport details using MRZ
* Perform **name matching across all documents**
* Perform **face verification (Passport ↔ Visa ↔ Photo)**
* Final output: **✅ Valid / ❌ Invalid with reason**

---

## 📂 Supported Documents

* Passport
* Visa
* Photograph
* 10th Memo
* 12th Memo
* Degree Certificate
and more...

---

## ⚙️ Tech Stack

* Python 3.10  
* Flask
* OpenCV
* EasyOCR
* DeepFace
* NumPy, Pillow
* Regex & NLP-based validation

---

## 🔄 Workflow

1. Upload document(s)
2. Preprocess image/PDF
3. Extract text using OCR
4. Classify document type
5. Extract name from passport (MRZ + text)
6. Verify name across all documents
7. Perform face comparison (3 images)
8. Return final result

---

## ▶️ How to Run

### 1. Install dependencies

```bash id="cmd1"
pip install -r requirements.txt
```

### 2. Run the app

```bash id="cmd2"
python app.py
```

### 3. Open in browser

```text id="url"
http://127.0.0.1:5000
```

---

## 📌 Output

* ✅ Valid
* ❌ Invalid (e.g., name mismatch / face mismatch / invalid document)

---

## ⚠️ Requirements

* Python 3.10
* Poppler (required for PDF processing)

👉 Install Poppler and add it to system PATH.

---

## 💡 Highlights

* OCR error-tolerant matching
* Works with real-world noisy documents
* Modular backend design
* Supports multiple document types

---

## 🔮 Future Improvements

* DOB verification across documents
* Passport number cross-check
* Confidence scoring system
* Frontend dashboard

---
