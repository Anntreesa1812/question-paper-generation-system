# pdf_ingest.py

import fitz
import pytesseract
from pdf2image import convert_from_bytes
import argparse
import json
import re
import os


# =====================================================
# PATH CONFIG
# =====================================================

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler\Library\bin"

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract_cmd = TESSERACT_PATH


# =====================================================
# DROP-CAP + LAYOUT FIX
# =====================================================

def fix_dropcaps(text: str) -> str:

    # Handles: \n\nD\n\neploying → Deploying
    text = re.sub(
        r"(?:\n\s*){1,3}([A-Z])(?:\n\s*){1,3}([a-z])",
        r"\1\2",
        text
    )

    return text


def repair_layout(text: str) -> str:

    # Fix hyphen breaks
    text = re.sub(r"-\n", "", text)

    text = fix_dropcaps(text)

    # Normalize multi-newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    lines = text.splitlines()

    merged = []
    buffer = ""

    for line in lines:

        line = line.strip()

        if not line:
            if buffer:
                merged.append(buffer)
                buffer = ""
            continue

        if buffer:
            buffer += " " + line
        else:
            buffer = line

    if buffer:
        merged.append(buffer)

    return "\n\n".join(merged)


# =====================================================
# REMOVE HEADERS / LAYOUT JUNK
# =====================================================

def remove_layout_noise(text: str) -> str:

    patterns = [
        r"\bPA\s*RT\s*ONE\b",
        r"\bC\s*H\s*A\s*P\s*T\s*E\s*R\s*\d+\b",
        r"\bWhy Biometrics\?\s*\d*\b",
    ]

    for p in patterns:
        text = re.sub(p, "", text, flags=re.I)

    return text


# =====================================================
# FINAL CLEAN
# =====================================================

def clean_text(text: str) -> str:

    text = repair_layout(text)

    text = remove_layout_noise(text)

    # Remove binary / diagram junk
    text = re.sub(r"[01]{6,}", "", text)

    # Remove junk lines
    text = re.sub(r"(?m)^[^a-zA-Z]{1,6}$", "", text)

    # Remove non-ascii
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\b(\d+)([A-Za-z])", r"\1. \2", text)
    text = re.sub(r"Username\s+Biometric.*?External System", "", text, flags=re.S)
    # Remove control chars
    text = re.sub(r"[\x00-\x1F\x7F]", " ", text)

    # Normalize bullets
    text = re.sub(r"\bu\s+", "- ", text)

    # Remove section/page headers
    text = re.sub(r"\d+\.\d+\s*/\s*.*?\d+", "", text)

    # Remove dense uppercase tables
    text = re.sub(r"(?:\b[A-Z ]{6,}\b\s*){5,}", "", text)

    return text.strip()


# =====================================================
# SAFE OCR
# =====================================================

def ocr_single_page(pdf_bytes, page_no):

    try:

        images = convert_from_bytes(
            pdf_bytes,
            dpi=250,
            poppler_path=POPPLER_PATH,
            first_page=page_no,
            last_page=page_no
        )

        return pytesseract.image_to_string(
            images[0],
            lang="eng",
            config="--psm 6"
        )

    except Exception as e:

        print(f">>> OCR failed on page {page_no}: {e}")
        return ""


# =====================================================
# HYBRID EXTRACTION
# =====================================================

def extract_pages(doc, pdf_bytes, start, end):

    pages = {}

    max_page = len(doc)

    for i in range(start, min(end + 1, max_page + 1)):

        page = doc[i - 1]

        blocks = page.get_text("blocks")

        final_text = ""

        for b in blocks:
            if b[6] == 0:
                final_text += b[4] + "\n"

        final_text = final_text.strip()

        # OCR fallback
        if len(final_text) < 150:

            print(f">>> OCR page {i}")
            final_text = ocr_single_page(pdf_bytes, i)

        pages[i] = final_text

    return pages


# =====================================================
# MAIN
# =====================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("pdf")
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)

    args = parser.parse_args()

    print(f">>> Processing pages {args.start} → {args.end}")


    with open(args.pdf, "rb") as f:
        pdf_bytes = f.read()

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")


    # Extract
    pages = extract_pages(
        doc,
        pdf_bytes,
        args.start,
        args.end
    )


    # Clean
    for p in pages:
        pages[p] = clean_text(pages[p])


    # Drop weak pages EARLY
    pages = {
        p: txt for p, txt in pages.items()
        if len(txt.strip()) >= 300
    }


    # Add markers (debug only)
    marked = {}

    for p, txt in pages.items():

        marked[p] = f"[PAGE {p}]\n\n{txt}\n\n"


    # Save JSON
    with open("D:\\text\\TIS\\Output\\pages_text.json", "w", encoding="utf-8") as f:

        json.dump(
            marked,
            f,
            indent=2,
            ensure_ascii=False
        )


    # Save readable debug
    with open("pages_debug.txt", "w", encoding="utf-8") as f:

        for p in sorted(marked):

            f.write(marked[p])
            f.write("\n" + "=" * 80 + "\n\n")


    print(f">>> Saved {len(marked)} pages successfully")


if __name__ == "__main__":
    main()