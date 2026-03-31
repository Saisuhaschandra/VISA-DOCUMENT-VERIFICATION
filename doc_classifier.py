import re

# Normalize text
def clean(text):
    return text.upper()


# Check passport
def is_passport(text):
    text = text.upper()
    score = 0

    # Country check
    if "INDIA" in text or "IND" in text:
        score += 1

    # Passport number
    if re.search(r'[A-Z]\s?[0-9]{7}', text):
        score += 2

    # Name
    if "GIVEN NAME" in text or "NAME" in text:
        score += 1

    # DOB
    if re.search(r'\d{2}[/-]\d{2}[/-]\d{4}', text):
        score += 1

    # MRZ
    if re.search(r'P<[A-Z]{3}', text):
        score += 3

    return score >= 3


# Fix OCR mistakes
def clean_ocr(text):
    text = text.upper()
    text = text.replace("O", "0")
    text = text.replace("I", "1")
    return text


# Check visa
def is_visa(text):
    text = clean_ocr(text)
    score = 0

    if "VISA" in text or "VISUM" in text:
        score += 2

    if "GERMANY" in text or "DEUTSCHLAND" in text:
        score += 2

    if re.search(r'[A-Z]\s?[0-9]{7}', text):
        score += 2

    if "ENJAMURI" in text or "CHANDRA" in text:
        score += 1

    if "P<" in text and "IND" in text:
        score += 3

    return score >= 4


# Check 10th
def is_tenth(text):
    text = clean(text)

    keywords = [
        "SSC",
        "SECONDARY SCHOOL",
        "BOARD OF SECONDARY",
        "MARKS MEMO",
        "GRADE",
        "CERTIFICATE"
    ]

    score = sum(1 for k in keywords if k in text)
    return score >= 2


# Check 12th
def is_twelfth(text):
    text = text.upper()
    score = 0

    if "INTER" in text:
        score += 1

    if "SECONDARY" in text:
        score += 1

    if "XII" in text or "12" in text:
        score += 1

    if "HSC" in text or "H S C" in text:
        score += 1

    if "MARKS" in text or "GRADE" in text:
        score += 1

    if "BOARD" in text:
        score += 1

    return score >= 2


# Check degree
def is_degree(text):
    text = text.upper()
    score = 0

    if "UNIV" in text or "UNIVERS" in text:
        score += 2

    if "SEMESTER" in text or "GRADE" in text or "SGPA" in text:
        score += 2

    if "CREDIT" in text or "SUBJECT" in text:
        score += 1

    if "PASSED" in text or "PASS" in text:
        score += 1

    if re.search(r'[A-Z]{3,}\s+[A-Z]{3,}', text):
        score += 1

    return score >= 3

#  ENGLISH TEST (IELTS / TOEFL / PTE) 
def is_english_score(text):

    text = text.upper()

    score = 0

    # keywords
    if "IELTS" in text or "TOEFL" in text or "PTE" in text:
        score += 2

    if "TEST REPORT" in text or "SCORE REPORT" in text:
        score += 1

    if "OVERALL" in text or "BAND" in text or "SCORE" in text:
        score += 1

    # score pattern
    if re.search(r'\d\.\d', text):   # 7.5, 6.0 etc
        score += 1

    return score >= 2
    
# Check bank statement
def is_bank(text):
    text = text.upper()
    score = 0

    if "BANK" in text:
        score += 2

    if "ACCOUNT" in text:
        score += 1

    if "STATEMENT" in text:
        score += 1

    if "DEPOSIT" in text or "WITHDRAWAL" in text:
        score += 2

    if "BALANCE" in text:
        score += 1

    if re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', text):
        score += 2
    elif re.search(r'\d{2}[-/]\d{2}[-/]\d{4}', text):
        score += 2

    if re.search(r'\d+\.\d{2}', text):
        score += 1

    return score >= 4


# Check SOP
def is_sop(text):
    text = clean(text)

    if "STATEMENT OF PURPOSE" in text:
        return True

    words = text.split()
    return len(words) > 200


# Check resume
def is_resume(text):
    text = clean(text)
    score = 0

    keywords = [
        "EDUCATION", "SKILLS", "PROJECTS",
        "EXPERIENCE", "OBJECTIVE", "PROFILE"
    ]

    score += sum(1 for k in keywords if k in text)

    if "EMAIL" in text or "@" in text:
        score += 1

    if re.search(r'\d{10}', text):
        score += 1

    return score >= 2


# Check ITR
def is_itr(text):
    text = clean(text)
    return "INCOME TAX" in text or "ITR" in text


# Check employment
def is_employment(text):
    text = clean(text)
    keywords = ["EMPLOYMENT", "COMPANY", "DESIGNATION", "SALARY"]
    return any(k in text for k in keywords)


# Check offer letter
def is_offer_letter(text):
    text = clean(text)
    keywords = ["OFFER LETTER", "OFFER", "POSITION", "JOINING"]
    return any(k in text for k in keywords)


# Check salary slip
def is_salary_slip(text):
    text = clean(text)
    keywords = ["SALARY", "PAYSLIP", "NET PAY", "EARNINGS"]
    return any(k in text for k in keywords)


# Check GST
def is_gst(text):
    text = clean(text)
    return "GST" in text or "GOODS AND SERVICES TAX" in text


# Check flight
def is_flight(text):
    text = clean(text)
    keywords = ["FLIGHT", "BOARDING", "PNR", "AIRLINE"]
    return any(k in text for k in keywords)


# Check hotel
def is_hotel(text):
    text = clean(text)
    keywords = ["HOTEL", "BOOKING", "CHECK-IN", "RESERVATION"]
    return any(k in text for k in keywords)


# Check insurance
def is_insurance(text):
    text = clean(text)
    keywords = ["INSURANCE", "POLICY", "COVERAGE"]
    return any(k in text for k in keywords)


# Photo (always true)
def is_photo(text):
    return True
