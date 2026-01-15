import fitz  # PyMuPDF
import re
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image

# 🔴 REQUIRED: Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# -------------------------------
# PDF TEXT EXTRACTION (TEXT + OCR)
# -------------------------------
def extract_text_from_pdf(uploaded_file):
    pdf_bytes = uploaded_file.file.read()

    # 1️⃣ Try normal text extraction
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    # 2️⃣ If text is too small → OCR fallback
    if len(text.strip()) < 50:
        images = convert_from_bytes(pdf_bytes)
        ocr_text = ""
        for img in images:
            ocr_text += pytesseract.image_to_string(img)
        return ocr_text

    return text


# -------------------------------
# MODULE-WISE SYLLABUS EXTRACTION
# -------------------------------
def extract_module_topics(text):
    modules = {}
    current_module = None

    ignore_keywords = [
        "course outcome",
        "course outcomes",
        "edition",
        "publisher",
        "textbook",
        "syllabus",
        "marks"
    ]

    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        # STOP parsing when References start
        if line.lower().startswith("references"):
            break

        # Detect Module headings
        match = re.match(r"Module\s+([IVX]+)", line, re.IGNORECASE)
        if match:
            current_module = f"Module {match.group(1)}"
            modules[current_module] = []
            continue

        if not current_module or len(line) < 5:
            continue

        lower_line = line.lower()
        if any(word in lower_line for word in ignore_keywords):
            continue

        # Split topics
        parts = re.split(r"[.,;-]", line)
        for part in parts:
            topic = part.strip()
            if len(topic) > 5:
                modules[current_module].append(topic)

    return modules
