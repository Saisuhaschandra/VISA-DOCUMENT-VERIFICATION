import os
import re
import json
from mrz_parser import extract_mrz, parse_mrz
from difflib import SequenceMatcher

TEXT_FOLDER = "extracted_text"
DEBUG_FILE = "debug_comparison.json"


def normalize(text):
    return re.sub(r'[^A-Z]', '', text.upper()) if text else ""


# ✅ FIXED MRZ NAME EXTRACTION (REMOVE COUNTRY CODE ONLY)
def extract_name_from_mrz(line1):

    if not line1:
        return None

    line1 = line1.upper()
    line1 = re.sub(r'\s+', '', line1)

    if not line1.startswith("P<"):
        return None

    try:
        # Remove "P<"
        line1 = line1[2:]

        # Remove country code (first 3 chars)
        country_code = line1[:3]
        name_part = line1[3:]

        parts = name_part.split("<<")

        if len(parts) < 2:
            return None

        surname = parts[0].replace("<", "")
        given = parts[1].replace("<", " ").strip()

        full_name = surname + " " + given

        print("MRZ COUNTRY CODE:", country_code)
        print("EXTRACTED NAME:", full_name)

        return full_name.strip()

    except Exception as e:
        print("MRZ ERROR:", e)
        return None


def extract_name_from_text(text):
    text = text.upper()
    lines = text.split("\n")

    candidates = []

    for line in lines:
        clean = re.sub(r'[^A-Z ]', '', line).strip()

        if len(clean) < 5:
            continue

        words = clean.split()

        if any(word in clean for word in [
            "VISA", "TYPE", "CLASS", "DATE", "BIRTH",
            "PASSPORT", "NUMBER", "NATIONALITY",
            "INDIA", "GOVERNMENT"
        ]):
            continue

        if 2 <= len(words) <= 4:
            candidates.append(clean)

    return max(candidates, key=len) if candidates else None


def name_match(n1, n2):

    if not n1 or not n2:
        return False

    def clean(text):
        text = text.upper()
        text = text.replace("0", "O")
        text = text.replace("1", "I")
        text = re.sub(r'[^A-Z ]', '', text)
        return text

    n1 = clean(n1)
    n2 = clean(n2)

    words1 = set(n1.split())
    words2 = set(n2.split())

    common = words1.intersection(words2)

    print("NAME1:", words1)
    print("NAME2:", words2)
    print("COMMON:", common)

    return len(common) >= 2


def name_present(name, text):
    return normalize(name) in normalize(text)


def extract_dob(text):
    match = re.search(r'\d{2}[/-]\d{2}[/-]\d{4}', text)
    return match.group() if match else None


def verify_documents():

    texts = {}

    files = [f for f in os.listdir(TEXT_FOLDER) if f.endswith(".txt")]

    if not files:
        return "❌ No documents uploaded"

    for file in files:
        doc_name = file.replace(".txt", "")
        with open(os.path.join(TEXT_FOLDER, file), "r", encoding="utf-8") as f:
            texts[doc_name] = f.read()

    passport_text = texts.get("passport")
    visa_text = texts.get("visa")

    if not passport_text:
        return "❌ Passport missing"

    if not visa_text:
        return "❌ Visa missing"

    p1, p2 = extract_mrz(passport_text)
    v1, v2 = extract_mrz(visa_text)

    if p1 and p2 and v1 and v2:

        def clean_mrz(text):
            text = text.upper().replace(" ", "")
            text = text.replace("O", "0").replace("I", "1")
            return text

        p_name = extract_name_from_mrz(p1)
        v_name = extract_name_from_mrz(v1)

        if not p_name:
            p_name = extract_name_from_text(passport_text)

        if not v_name:
            v_name = extract_name_from_text(visa_text)

        if not name_match(p_name, v_name):
            return "❌ Name mismatch (passport vs visa)"

        p_mrz = clean_mrz(p1 + p2)
        v_mrz = clean_mrz(v1 + v2)

        score = SequenceMatcher(None, p_mrz, v_mrz).ratio()

        print("MRZ similarity:", score)

        if score < 0.75:
            return "❌ MRZ mismatch (passport vs visa)"

        base_name = p_name

    else:
        p_name = extract_name_from_text(passport_text)
        v_name = extract_name_from_text(visa_text)

        if not p_name or not v_name:
            return "❌ Could not extract names"

        if not name_match(p_name, v_name):
            return "❌ Passport & Visa name mismatch"

        base_name = p_name

    for doc, text in texts.items():

        if doc in ["passport", "visa"]:
            continue

        if not text or len(text) < 20:
            return f"❌ {doc} is invalid"

        # ---------- FULL NAME FIRST ----------
        name_words = normalize(base_name).split()
        text_clean = normalize(text)

        full_match = all(word in text_clean for word in name_words)

        # ---------- PARTIAL FALLBACK ----------
        if not full_match:
            text_words = set(text_clean.split())
            common = set(name_words).intersection(text_words)

            print("FULL MATCH FAILED → PARTIAL CHECK")
            print("NAME WORDS:", name_words)
            print("COMMON WORDS:", common)

            if len(common) < 2:
                return f"❌ Name mismatch in {doc}"

        if doc == "twelfth":
            p_dob = extract_dob(passport_text)
            t_dob = extract_dob(text)

            print("Passport DOB:", p_dob)
            print("12th DOB:", t_dob)

            # OPTIONAL CHECK ONLY (NO FAILURE)
            if p_dob and t_dob:
                if p_dob == t_dob:
                    print("DOB MATCH ✔")
                else:
                    print("DOB MISMATCH (IGNORED)")

        if doc == "sop":
            if len(text.split()) < 100:
                return "❌ SOP too short"

        if doc == "bank":
            if len(text) < 50:
                return "❌ Invalid bank statement"

    return "✅ Verified"


def save_debug(data):
    with open(DEBUG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
