import easyocr
import os

reader = easyocr.Reader(['en'])

TEXT_FOLDER = "extracted_text"
os.makedirs(TEXT_FOLDER, exist_ok=True)


def extract_text(image_path, doc_type):

    print("Running EasyOCR for:", doc_type)

    results = reader.readtext(image_path)

    text = ""

    for (_, txt, _) in results:
        text += txt + "\n"

    save_path = os.path.join(TEXT_FOLDER, f"{doc_type}.txt")

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(text)

    print("Saved:", save_path)

    return text
