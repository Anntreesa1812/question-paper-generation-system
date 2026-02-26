import sys
import os
import re
import json
import pdfplumber


# ---------------------------------------
# Read PDF
# ---------------------------------------

def read_pdf(path):

    text = ""

    with pdfplumber.open(path) as pdf:

        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"

    return text


# ---------------------------------------
# Clean text
# ---------------------------------------

def clean_text(text):

    text = re.sub(r"\s+", " ", text)

    text = text.replace(" ,", ",")
    text = text.replace(" .", ".")

    return text.strip()


# ---------------------------------------
# Extract modules
# ---------------------------------------

def extract_modules(text):

    pattern = re.compile(
        r"(module\s+[ivx]+)(.*?)(?=module\s+[ivx]+|references|$)",
        re.IGNORECASE
    )

    matches = pattern.findall(text)

    modules = {}

    for title, content in matches:

        name = title.strip().upper()

        modules[name] = content.strip()

    return modules


# ---------------------------------------
# Extract topics
# ---------------------------------------

def extract_topics(module_text):

    # Remove hour info
    module_text = re.sub(
        r"\d+\s*hours?",
        "",
        module_text,
        flags=re.I
    )

    # Normalize unicode dashes
    module_text = module_text.replace("–", "-")
    module_text = module_text.replace("—", "-")

    # Protect technical hyphen words
    protected = {
        "miller-rabin": "MILLER_RABIN",
        "diffie-hellman": "DIFFIE_HELLMAN",
        "sha-512": "SHA_512",
        "s-box": "S_BOX",
        "e-mail": "E_MAIL",
        "x.509": "X509"
    }

    lower = module_text.lower()

    for k, v in protected.items():
        lower = lower.replace(k, v)

    module_text = lower


    # Split only on safe separators
    parts = re.split(
        r",|\.\s+|;\s+|\s-\s+|\n",
        module_text
    )

    topics = []

    for p in parts:

        t = p.strip(" .:-\n\t")

        if len(t) < 4:
            continue

        if re.fullmatch(r"\d+", t):
            continue

        if t in ["and", "or", "the"]:
            continue

        # Restore protected words
        for k, v in protected.items():
            t = t.replace(v.lower(), k)

        # Capitalize nicely
        t = t.title()

        topics.append(t)

    return topics

    

# ---------------------------------------
# Parse syllabus
# ---------------------------------------

def parse_syllabus(text):

    text = clean_text(text)

    modules = extract_modules(text)

    syllabus = {}

    for module, content in modules.items():

        topics = extract_topics(content)

        syllabus[module] = topics

    return syllabus


# ---------------------------------------
# Save output
# ---------------------------------------

def save_text(syllabus, path):

    with open(path, "w", encoding="utf-8") as f:

        for module, topics in syllabus.items():

            f.write(f"{module}:\n")

            for t in topics:
                f.write(f"  - {t}\n")

            f.write("\n")


def save_json(syllabus, path):

    with open(path, "w", encoding="utf-8") as f:

        json.dump(
            syllabus,
            f,
            indent=2,
            ensure_ascii=False
        )


# ---------------------------------------
# Main
# ---------------------------------------

def main():

    if len(sys.argv) < 2:

        print("Usage: python syllabus_parser_pdf.py <syllabus.pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not os.path.exists(pdf_path):

        print("File not found:", pdf_path)
        sys.exit(1)

    print("\n[1] Reading PDF...")

    text = read_pdf(pdf_path)

    if len(text.strip()) < 200:
        print("⚠️ Warning: Very little text extracted (may be scanned PDF)")

    print("[2] Parsing syllabus...")

    syllabus = parse_syllabus(text)

    print("[3] Modules found:", len(syllabus))

    out_txt = "syllabus_parsed.txt"
    out_json = "syllabus_parsed.json"

    save_text(syllabus, out_txt)
    save_json(syllabus, out_json)

    print("\n✅ Saved:")
    print(" -", out_txt)
    print(" -", out_json)


# ---------------------------------------

if __name__ == "__main__":
    main()