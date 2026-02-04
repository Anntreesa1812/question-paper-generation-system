import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_bytes

# -------------------------------
# REQUIRED SYSTEM PATHS
# -------------------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler\Library\bin"


# -------------------------------
# TEXT QUALITY VALIDATION
# -------------------------------
def is_valid_extracted_text(text: str) -> bool:
    """
    Detects and rejects fake / hidden text layers
    commonly found in scanned textbooks.
    """
    if not text or len(text.strip()) < 300:
        return False

    lower_text = text.lower()

    # Known garbage / hidden text patterns
    garbage_patterns = [
        "hidden page",
        "this page intentionally left blank",
        "digitized by",
        "scanned by",
        "copyright",
    ]

    for pattern in garbage_patterns:
        if lower_text.count(pattern) > 3:
            return False

    words = text.split()
    unique_words = set(words)

    # Vocabulary diversity check
    diversity_ratio = len(unique_words) / max(len(words), 1)

    if diversity_ratio < 0.25:
        return False

    return True


# -------------------------------
# MAIN INGESTION FUNCTION
# -------------------------------
def extract_text_from_pdf(uploaded_file):
    print(">>> extract_text_from_pdf CALLED")

    pdf_bytes = uploaded_file.file.read()
    uploaded_file.file.seek(0)

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    extracted_text = ""

    for page in doc:
        extracted_text += page.get_text("text") + "\n"

    if is_valid_extracted_text(extracted_text):
        return extracted_text

    print(">>> FORCING OCR NOW")

    images = convert_from_bytes(
        pdf_bytes,
        dpi=200,
        poppler_path=POPPLER_PATH
    )

    ocr_text = ""
    for i, img in enumerate(images):
        print(f">>> OCR page {i+1}/{len(images)}")
        ocr_text += pytesseract.image_to_string(img, lang="eng") + "\n"

    return ocr_text
