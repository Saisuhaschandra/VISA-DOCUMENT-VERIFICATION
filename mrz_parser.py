import re

# Extract MRZ lines
def extract_mrz(text):

    lines = text.split("\n")
    mrz_lines = []

    for line in lines:
        line = line.strip().upper()

        if len(line) < 25:
            continue

        if "<" in line:
            mrz_lines.append(line)

    if len(mrz_lines) >= 2:
        return mrz_lines[-2], mrz_lines[-1]

    return None, None


# Extract name from MRZ
def extract_name_from_mrz(line1):

    if not line1:
        return None

    line1 = line1.upper().strip()

    if not line1.startswith("P<"):
        return None

    try:
        # Remove P<
        line1 = line1[2:]

        # Remove country code
        name_part = line1[3:]

        parts = name_part.split("<<")

        if len(parts) < 2:
            return None

        surname = parts[0].replace("<", "").strip()
        given_names = parts[1].replace("<", " ").strip()

        # Keep only valid words
        def valid_word(w):
            return w.isalpha() and len(w) > 1

        given_words = [w for w in given_names.split() if valid_word(w)]

        full_name = surname + " " + " ".join(given_words)

        print("MRZ NAME:", full_name)

        return full_name

    except Exception as e:
        print("MRZ parse error:", e)
        return None


# Extract name from normal OCR text
def extract_name_from_text(text):

    lines = text.upper().split("\n")
    name_parts = []
    capture = False

    for line in lines:

        if "GIVEN NAME" in line or "GIVEN NAMELS" in line:
            capture = True
            continue

        if capture:
            if len(line.strip()) < 2:
                break

            if "DATE" in line or "SEX" in line:
                break

            name_parts.append(line.strip())

    # Clean extracted name
    if name_parts:
        raw_name = " ".join(name_parts)

        words = raw_name.split()
        clean_words = [w for w in words if w.isalpha() and len(w) > 1]

        return " ".join(clean_words)

    return None


# Choose best name between MRZ and text
def choose_best_name(mrz_name, text_name):

    if not mrz_name:
        return text_name

    if not text_name:
        return mrz_name

    # Keep only valid words
    def valid_word(w):
        return w.isalpha() and len(w) > 1

    mrz_words = [w for w in mrz_name.split() if valid_word(w)]
    text_words = [w for w in text_name.split() if valid_word(w)]

    final_words = []

    for t_word in text_words:
        best_match = t_word

        for m_word in mrz_words:
            if t_word in m_word or m_word in t_word:
                best_match = t_word
                break

        final_words.append(best_match)

    final_name = " ".join(final_words)

    print("MRZ NAME:", mrz_name)
    print("TEXT NAME:", text_name)
    print("FINAL NAME:", final_name)

    return final_name
