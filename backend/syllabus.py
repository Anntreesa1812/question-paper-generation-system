from pydoc import doc, text
import fitz  # PyMuPDF
import re
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import logging

# 🔴 REQUIRED: Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def is_image_based_pdf(doc):
    for page in doc:
        # If ANY page has extractable text, it's NOT image-based
        if page.get_text("text").strip():
            return False
    return True



# -------------------------------
# PDF TEXT EXTRACTION (TEXT + OCR)
# -------------------------------
def extract_text_from_pdf(uploaded_file):
    pdf_bytes = uploaded_file.file.read()
    logger.debug(f"PDF size: {len(pdf_bytes)} bytes")

    # ---- Try PyMuPDF first ----
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""

    for page in doc:
        text += page.get_text("text") + "\n"

    logger.debug(f"PyMuPDF extracted text length: {len(text)}")

    # ---- If text is meaningful AND not empty, return it ----
    if text.strip() and len(text.strip()) > 100:
        logger.debug("Returning PyMuPDF text")
        return text

    # ---- OCR fallback (for scanned PDFs or non-selectable text) ----
    logger.debug("Falling back to OCR...")
    from pdf2image import convert_from_bytes
    images = convert_from_bytes(pdf_bytes, dpi=300)
    logger.debug(f"Converted {len(images)} pages to images")

    ocr_text = ""
    for i, img in enumerate(images):
        page_text = pytesseract.image_to_string(img, lang="eng")
        logger.debug(f"Page {i} OCR text length: {len(page_text)}")
        ocr_text += page_text

    logger.debug(f"Total OCR text length: {len(ocr_text)}")
    return ocr_text if ocr_text.strip() else text



# -------------------------------
# MODULE-WISE SYLLABUS EXTRACTION
# -------------------------------
def extract_module_topics(text):
    logger.debug(f"extract_module_topics received text length: {len(text)}")
    logger.debug(f"First 500 chars: {text[:500]}")
    
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
    logger.debug(f"Total lines: {len(lines)}")

    for line in lines:
        line = line.strip()

        # STOP parsing when References start
        if line.lower().startswith("references"):
            logger.debug("Stopped at References")
            break

        # Detect Module headings - handles both "Module I" and "Module 1"
        match = re.match(r"Module\s+([IVX0-9]+|[0-9]+)", line, re.IGNORECASE)
        if match:
            current_module = f"Module {match.group(1)}"
            modules[current_module] = []
            logger.debug(f"Found: {current_module}")
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

    logger.debug(f"Extracted modules: {modules}")
    return modules
