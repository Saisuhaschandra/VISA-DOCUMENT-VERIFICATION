import re
from deepface import DeepFace
from doc_classifier import *
from mrz_parser import extract_mrz, extract_name_from_mrz, extract_name_from_text, choose_best_name


#  NAME MATCH 
def name_present(name, text):

    if not name or not text:
        return False

    name_words = name.upper().split()
    text_words = set(text.upper().split())

    common = [w for w in name_words if w in text_words]

    match_ratio = len(common) / len(name_words)

   # print("\n--- NAME CHECK ---")
    #print("NAME:", name_words)
    #print("COMMON:", common)
    #print("MATCH RATIO:", match_ratio)

    #  FLEXIBLE THRESHOLD 
    if len(name_words) >= 3:
        return match_ratio >= 0.6   # 60% match
    else:
        return match_ratio >= 0.5


#  FACE MATCH 
def verify_faces(passport_img, visa_img, photo_img):

    try:
        # passport vs visa
        r1 = DeepFace.verify(
            img1_path=passport_img,
            img2_path=visa_img,
            model_name="SFace",
            enforce_detection=True
        )

        # passport vs photo
        r2 = DeepFace.verify(
            img1_path=passport_img,
            img2_path=photo_img,
            model_name="SFace",
            enforce_detection=True
        )

        print("\nFace Results:")
        print("Passport vs Visa:", r1["verified"], r1["distance"])
        print("Passport vs Photo:", r2["verified"], r2["distance"])

        return r1["verified"] and r2["verified"]

    except Exception as e:
        print("Face error:", e)
        return False


#  MAIN VERIFY 
def verify_documents(uploaded_images, texts):

    if not texts:
        return "❌ No documents uploaded"

    #  CLASSIFICATION 
    for doc_name, text in texts.items():

        func_name = f"is_{doc_name}"

        if func_name in globals():
            is_valid = globals()[func_name](text)
        else:
            is_valid = False

        # skip photo (no OCR)
        if doc_name != "photo" and not is_valid:
            return f"❌ Invalid {doc_name}"

    #  PASSPORT NAME 
    passport_text = texts.get("passport")

    if not passport_text:
        return "❌ Passport required"

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

    if not passport_img or not visa_img or not photo_img:
        return "❌ Upload passport, visa, and photo"

    print("\nRunning Face Verification...")

    if not verify_faces(passport_img, visa_img, photo_img):
        return "❌ Face mismatch"

    #  Final result
    return "✅ Valid"
