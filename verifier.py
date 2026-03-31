import re
from deepface import DeepFace
from doc_classifier import *
from mrz_parser import extract_mrz, extract_name_from_mrz, extract_name_from_text, choose_best_name
from datetime import datetime


#  EXTRACT EXPIRY 
def extract_expiry_date(text):

    lines = text.upper().split("\n")
    date_candidates = []

    for i, line in enumerate(lines):

        if "EXPIRY" in line:

            # collect nearby lines (OCR-safe)
            for j in range(i + 1, min(i + 6, len(lines))):

                matches = re.findall(r'\d{2}/\d{2}/\d{4}', lines[j])

                for m in matches:
                    date_candidates.append(m)

    print("EXPIRY CANDIDATES:", date_candidates)

    if not date_candidates:
        return None

    # picks latest date
    def to_date(d):
        return datetime.strptime(d, "%d/%m/%Y")

    expiry_date = max(date_candidates, key=to_date)

    print("FINAL EXPIRY:", expiry_date)

    return expiry_date


#  VALIDATE EXPIRY 
def is_passport_valid(expiry_date):

    try:
        expiry = datetime.strptime(expiry_date, "%d/%m/%Y")
        today = datetime.today()

        print("TODAY:", today.strftime("%d/%m/%Y"))
        print("EXPIRY:", expiry_date)

        return expiry > today

    except Exception as e:
        print("Date parsing error:", e)
        return False


#  NAME MATCH 
def name_present(name, text):

    if not name or not text:
        return False

    name_words = name.upper().split()
    text_words = set(text.upper().split())

    common = [w for w in name_words if w in text_words]

    match_ratio = len(common) / len(name_words)

    print("\n--- NAME CHECK ---")
    print("NAME:", name_words)
    print("COMMON:", common)
    print("MATCH RATIO:", match_ratio)

    if len(name_words) >= 3:
        return match_ratio >= 0.6
    else:
        return match_ratio >= 0.5


#  DYNAMIC FACE MATCH 
def verify_faces_dynamic(passport_img, visa_img, photo_img):

    pairs = []

    if passport_img and visa_img:
        pairs.append((passport_img, visa_img))

    if passport_img and photo_img:
        pairs.append((passport_img, photo_img))

    if visa_img and photo_img:
        pairs.append((visa_img, photo_img))

  
    if len(pairs) == 0:
        print("No face pairs to compare")
        return True

    print("\nRunning Face Verification on", len(pairs), "pairs")

    for i, (a, b) in enumerate(pairs):

        try:
            result = DeepFace.verify(
                img1_path=a,
                img2_path=b,
                model_name="SFace",
                enforce_detection=True
            )

            print(f"\nPair {i+1}: {a} vs {b}")
            print("Match:", result["verified"])
            print("Distance:", result["distance"])

            if not result["verified"]:
                return False

        except Exception as e:
            print("Face error:", e)
            return False

    return True


#  MAIN VERIFY 
def verify_documents(uploaded_images, texts):

    if not texts:
        return "❌ No documents uploaded"

    #  MANDATORY DOCUMENTS 
    if "passport" not in texts:
        return "❌ Passport required"

    if "english_score" not in texts:
        return "❌ IELTS/TOEFL/PTE scorecard required"

    #  CLASSIFICATION 
    for doc_name, text in texts.items():

        func_name = f"is_{doc_name}"

        if func_name in globals():
            is_valid = globals()[func_name](text)
        else:
            is_valid = False

        # skip photo (no OCR validation)
        if doc_name != "photo" and not is_valid:
            return f"❌ Invalid {doc_name}"

    #  PASSPORT 
    passport_text = texts.get("passport")

    #  EXPIRY CHECK 
    expiry_date = extract_expiry_date(passport_text)

    if not expiry_date:
        return "❌ Could not extract passport expiry date"

    if not is_passport_valid(expiry_date):
        return "❌ Passport expired"

    #  NAME EXTRACTION 
    p1, p2 = extract_mrz(passport_text)

    mrz_name = extract_name_from_mrz(p1)
    text_name = extract_name_from_text(passport_text)

    passport_name = choose_best_name(mrz_name, text_name)

    print("\nFINAL PASSPORT NAME:", passport_name)

    #  NAME CHECK 
    for doc_name, text in texts.items():

        if doc_name in ["passport", "photo"]:
            continue

        if not name_present(passport_name, text):
            return f"❌ Name mismatch in {doc_name}"

    #  FACE MATCH 
    passport_img = uploaded_images.get("passport")
    visa_img = uploaded_images.get("visa")
    photo_img = uploaded_images.get("photo")

    print("\n--- FACE DEBUG ---")
    print("passport:", passport_img)
    print("visa:", visa_img)
    print("photo:", photo_img)

    if not verify_faces_dynamic(passport_img, visa_img, photo_img):
        return "❌ Face mismatch"

    #  FINAL 
    return "✅ Valid"
