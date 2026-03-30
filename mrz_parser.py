import re


# ---------- EXTRACT MRZ LINES ----------
def extract_mrz(text):

    lines = text.split("\n")

    mrz_lines = []

    for line in lines:
        line = line.strip()

        # MRZ lines are long + contain "<"
        if "<" in line and len(line) > 30:
            mrz_lines.append(line)

    if len(mrz_lines) >= 2:
        return mrz_lines[-2], mrz_lines[-1]

    return None, None


# ---------- PARSE MRZ ----------
def parse_mrz(line1, line2):

    data = {}

    try:
        # ---------- NAME ----------
        name_part = line1.split("<<")
        surname = name_part[0].split("<")[-1]
        given_names = name_part[1].replace("<", " ")

        data["name"] = (surname + " " + given_names).strip()

        # ---------- PASSPORT NUMBER ----------
        passport_number = re.findall(r'[A-Z0-9]{8,9}', line2)
        if passport_number:
            data["passport_number"] = passport_number[0]

    except Exception as e:
        print("MRZ parse error:", e)

    return data