# VISA-DOCUMENT-VERIFICATION AI

A backend system that verifies user documents using **OCR, MRZ parsing, and face recognition** to ensure all documents belong to the same person.

---

## 🚀 Features

* Upload and verify multiple documents
* OCR-based text extraction (EasyOCR)
* Passport verification using MRZ
* Name matching across documents
* Passport expiry validation (supports multiple date formats)
* Dynamic face verification (Passport ↔ Visa ↔ Photo)
* Final result: **✅ Valid / ❌ Invalid**

---

## 📂 Supported Documents

* Passport
* Visa
* Photograph
* 10th Memo
* 12th Memo
* Degree Certificate

  
more..

---

## ⚙️ Tech Stack

* Python 3.10
* Flask
* OpenCV
* EasyOCR
* DeepFace

---

## 🔄 Workflow

1. Upload document(s)
2. Preprocess & extract text (OCR)
3. Classify document type
4. Extract name (MRZ + text)
5. Verify name across documents
6. Validate passport expiry
7. Perform face comparison
8. Return final result

---

## ▶️ Run Project

```bash
pip install -r requirements.txt
python app.py
```

Open:

```
http://127.0.0.1:5000
```

---

## 📌 Output

* ✅ Valid
* ❌ Invalid (name mismatch / face mismatch / expired passport)

---

## 💡 Highlights

* OCR error-tolerant logic
* Supports real-world document formats
* Dynamic verification (no fixed document requirement)

---

