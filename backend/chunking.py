import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_bytes
import logging

# 🔴 REQUIRED: Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# -------------------------------
# PDF TEXT EXTRACTION (TEXT + OCR)
# -------------------------------
def extract_text_from_pdf(uploaded_file):
    pdf_bytes = uploaded_file.file.read()
    logger.debug(f"Chunking: PDF size: {len(pdf_bytes)} bytes")

    # ---- Try PyMuPDF first ----
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""

    for page in doc:
        text += page.get_text("text") + "\n"

    logger.debug(f"Chunking: PyMuPDF extracted text length: {len(text)}")

    # ---- If text is meaningful AND not empty, return it ----
    if text.strip() and len(text.strip()) > 100:
        logger.debug("Chunking: Returning PyMuPDF text")
        return text

    # ---- OCR fallback (for scanned PDFs or non-selectable text) ----
    logger.debug("Chunking: Falling back to OCR...")
    images = convert_from_bytes(pdf_bytes, dpi=300)
    logger.debug(f"Chunking: Converted {len(images)} pages to images")

    ocr_text = ""
    for i, img in enumerate(images):
        page_text = pytesseract.image_to_string(img, lang="eng")
        logger.debug(f"Chunking: Page {i} OCR text length: {len(page_text)}")
        ocr_text += page_text + "\n"

    logger.debug(f"Chunking: Total OCR text length: {len(ocr_text)}")
    return ocr_text if ocr_text.strip() else text


# -------------------------------
# TEXT CHUNKING
# -------------------------------
def chunk_text(text, chunk_size=200):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk.strip()) > 50:
            chunks.append(chunk)

    return chunks

