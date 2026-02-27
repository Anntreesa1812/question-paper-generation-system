import fitz  # PyMuPDF
import re
import json
import sys
import os
from collections import OrderedDict


# =========================================================
# 1️⃣ READ PDF (Layout-aware)
# =========================================================

def read_pdf(path):
    doc = fitz.open(path)
    full_text = ""

    for page in doc:
        blocks = page.get_text("blocks")
        blocks = sorted(blocks, key=lambda b: (b[1], b[0]))

        for block in blocks:
            text = block[4].strip()
            if text:
                full_text += text + "\n"

    doc.close()
    return full_text


# =========================================================
# 2️⃣ CLEAN TEXT
# =========================================================

def clean_text(text):

    # Fix broken unicode artifacts
    text = text.replace("￾", "")
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Remove References section
    text = re.split(r"references\s*:", text, flags=re.I)[0]

    # Normalize whitespace
    text = re.sub(r"\r", "", text)
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


# =========================================================
# 3️⃣ EXTRACT COURSE TITLE + CODE
# =========================================================

def extract_course_info(text):

    lines = text.split("\n")

    if not lines:
        return "", ""

    first_line = lines[0]

    code_match = re.search(r"\b\d{2}-\d{3}-\d{4}\b", first_line)
    course_code = code_match.group() if code_match else ""

    course_title = first_line.replace(course_code, "").strip()

    return course_title, course_code


# =========================================================
# 4️⃣ EXTRACT MODULES
# =========================================================

def extract_modules(text):

    pattern = re.compile(
        r"(module\s+[ivx]+)(.*?)(?=module\s+[ivx]+|$)",
        re.I | re.S
    )

    matches = pattern.findall(text)

    modules = OrderedDict()

    for title, content in matches:
        modules[title.upper()] = content.strip()

    return modules


# =========================================================
# 5️⃣ EXTRACT TOPICS
# =========================================================

def extract_topics(module_text):

    # Replace newline with comma separator
    module_text = module_text.replace("\n", " , ")

    # Split on comma and dash separators
    parts = re.split(r",|\s-\s", module_text)

    topics = []
    seen = set()

    for part in parts:
        t = part.strip(" .:-").lower()

        if len(t) < 3:
            continue

        if re.fullmatch(r"\d+", t):
            continue

        if t in seen:
            continue

        seen.add(t)
        topics.append(t.title())

    return topics


# =========================================================
# 6️⃣ BUILD STRUCTURED OUTPUT
# =========================================================

def build_structure(text):

    text = clean_text(text)

    course_title, course_code = extract_course_info(text)
    modules = extract_modules(text)

    structured = {
        "course_title": course_title,
        "course_code": course_code,
        "modules": OrderedDict()
    }

    for module_name, module_content in modules.items():

        topics = extract_topics(module_content)

        # This is what SBERT will embed
        embedding_ready_text = " ".join(topics)

        structured["modules"][module_name] = {
            "raw_text": module_content,
            "topics": topics,
            "embedding_ready_text": embedding_ready_text
        }

    return structured


# =========================================================
# 7️⃣ MAIN
# =========================================================

def main():

    if len(sys.argv) < 2:
        print("Usage: python syllabus_parser.py <syllabus.pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not os.path.exists(pdf_path):
        print("File not found.")
        sys.exit(1)

    print("Reading syllabus...")
    text = read_pdf(pdf_path)

    print("Parsing structure...")
    structured = build_structure(text)

    print("Modules detected:", len(structured["modules"]))

    output_file = "D:\\text\\SIS\\Output_Json\\structured_syllabus.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2, ensure_ascii=False)

    print("Saved:", output_file)


if __name__ == "__main__":
    main()