import re
import cv2
# ---------- NORMALIZE ----------
def clean(text):
    return text.upper()


# ---------- PASSPORT ----------
def is_passport(text):
    text = text.upper()
    score = 0

    if "INDIA" in text or "IND" in text:
        score += 1

    if re.search(r'[A-Z]\s?[0-9]{7}', text):
        score += 2

    if "GIVEN NAME" in text or "NAME" in text:
        score += 1

    if re.search(r'\d{2}[/-]\d{2}[/-]\d{4}', text):
        score += 1

    if re.search(r'P<[A-Z]{3}', text):
        score += 3

    return score >= 3


# ---------- OCR CLEAN ----------
def clean_ocr(text):
    text = text.upper()
    text = text.replace("O", "0")
    text = text.replace("I", "1")
    return text


# ---------- VISA ----------
import re


def is_visa(text):

    if not text:
        return False

    text = text.upper()

    # small OCR fixes
    text = text.replace("@", "A").replace("0", "O").replace("1", "I")

    score = 0

    # main keyword
    if "VISA" in text:
        score += 2

    # common fields
    if "SURNAME" in text or "GIVEN NAME" in text:
        score += 1

    if "PASSPORT" in text:
        score += 1

    if "NATIONALITY" in text:
        score += 1

    if "BIRTH" in text or "DOB" in text:
        score += 1

    if "ISSUE" in text:
        score += 1

    if "EXPIR" in text:
        score += 1

    # MRZ pattern (long line with many '<')
    for line in text.split("\n"):
        line = line.strip()
        if len(line) > 30 and line.count("<") >= 5:
            score += 3
            break

    # passport-like number
    if re.search(r'[A-Z0-9]{7,9}', text):
        score += 1

    return score >= 4


# ---------- PHOTO ----------


def is_photo(text, image_path=None):

    # ---------- IMAGE CHECK FIRST (PRIORITY) ----------
    if image_path:
        img = cv2.imread(image_path)

        if img is None:
            return False

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(gray, 50, 150)
        edge_density = edges.mean()

        # 🔥 Photos usually have LOW edge density
        if edge_density < 25:
            return True

    # ---------- FALLBACK TEXT CHECK ----------
    if len(text.strip()) < 50:
        return True

    return False


# ---------- 10TH ----------
def is_tenth(text):

    text = text.upper()
    score = 0
    # strong indicators (10th specific)
    if "SSC" in text or "SECONDARY SCHOOL CERTIFICATE" in text:
        score += 3

    if "CLASS X" in text or "10TH" in text:
        score += 2

    # general indicators
    if "BOARD" in text:
        score += 1

    if "MARKS" in text:
        score += 1

    if "INTER" in text or "12TH" in text or "HSC" in text:
        return False

    return score >= 3

# ---------- 12TH ----------
def is_twelfth(text):

    text = text.upper()

    # ---------- MAIN KEYWORDS ----------
    if "INTER" in text and "BOARD" in text:
        return True

    # ---------- SUBJECT CHECK ----------
    if ("MATHEMATICS" in text and 
        "PHYSICS" in text and 
        "CHEMISTRY" in text):
        return True

    # ---------- YEAR / EXAM ----------
    if "SECOND YEAR" in text or "IPE" in text:
        return True

    # ---------- NEGATIVE FILTER ----------
    if "SSC" in text or "10TH" in text:
        return False

    return False
# ---------- DEGREE ----------
def is_degree(text):
    text = clean(text)
    score = 0

    # Degree keywords
    if "BACHELOR" in text or "MASTER" in text or "DEGREE" in text:
        score += 2

    if "TECHNOLOGY" in text or "ENGINEERING" in text:
        score += 2

    # University / institute
    if "UNIVERSITY" in text or "INSTITUTE" in text:
        score += 1

    # Optional supporting words
    if "AWARDED" in text or "CONFERS" in text:
        score += 1

    return score >= 3


# ---------- BANK ----------
def is_bank(text):
    text = clean(text)
    score = 0

    if "BANK" in text:
        score += 2
    if "ACCOUNT" in text:
        score += 1
    if "STATEMENT" in text:
        score += 1
    if "BALANCE" in text:
        score += 1
    if re.search(r'\d+\.\d{2}', text):
        score += 1

    return score >= 4


# ---------- SOP ----------
def is_sop(text):
    text = clean(text)
    score = 0

    if "recommendation" in text:
        score += 2
    if "letter" in text:
        score += 1
    if "STATEMENT" in text:
        score += 1
    if "master" in text:
        score += 1
    if re.search(r'\d+\.\d{2}', text):
        score += 1

    return score >= 3

# ---------- RESUME ----------
def is_resume(text):
    text = clean(text)
    keywords = ["EDUCATION", "SKILLS", "EXPERIENCE"]
    score = sum(1 for k in keywords if k in text)

    if "@" in text:
        score += 1

    return score >= 2



# ---------- ITR ----------
def is_itr(text):
    text = clean(text)
    keywords = ["INCOME TAX", "ITR", "ASSESSMENT YEAR", "PAN", "TOTAL INCOME"]
    return sum(1 for k in keywords if k in text) >= 2


# ---------- EMPLOYMENT ----------
def is_employment(text):
    text = clean(text)
    keywords = ["EMPLOYMENT", "COMPANY", "DESIGNATION", "EMPLOYEE", "SALARY"]
    return sum(1 for k in keywords if k in text) >= 2


# ---------- OFFER LETTER ----------
def is_offer_letter(text):
    text = clean(text)
    keywords = ["OFFER LETTER", "CONGRATULATIONS", "POSITION", "JOINING DATE"]
    return sum(1 for k in keywords if k in text) >= 2


# ---------- SALARY SLIP ----------
def is_salary_slip(text):
    text = clean(text)
    keywords = ["SALARY", "PAY SLIP", "NET PAY", "EARNINGS", "DEDUCTIONS"]
    return sum(1 for k in keywords if k in text) >= 2


# ---------- GST ----------
def is_gst(text):
    text = clean(text)
    keywords = ["GST", "GOODS AND SERVICES TAX", "GSTIN", "REGISTRATION"]
    return sum(1 for k in keywords if k in text) >= 2


# ---------- FLIGHT ----------
def is_flight(text):
    text = clean(text)
    keywords = ["FLIGHT", "PNR", "BOARDING", "DEPARTURE", "ARRIVAL"]
    return sum(1 for k in keywords if k in text) >= 2


# ---------- HOTEL ----------
def is_hotel(text):
    text = clean(text)
    keywords = ["HOTEL", "BOOKING", "CHECK-IN", "CHECK-OUT", "RESERVATION"]
    return sum(1 for k in keywords if k in text) >= 2


# ---------- INSURANCE ----------
def is_insurance(text):
    text = clean(text)
    keywords = ["INSURANCE", "POLICY", "COVERAGE", "PREMIUM", "INSURED"]
    return sum(1 for k in keywords if k in text) >= 2
