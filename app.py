import streamlit as st
import fitz  # PyMuPDF
import nltk
import pandas as pd
import re
import json

from nltk.corpus import stopwords

nltk.download("stopwords")

# -------------------------------------------------
# PDF TEXT EXTRACTION
# -------------------------------------------------
def extract_text_from_pdf(pdf_file):
    text = ""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    return text


# -------------------------------------------------
# MODULE-WISE SYLLABUS TOPIC EXTRACTION (RULE-BASED)
# -------------------------------------------------
def extract_module_topics(text):
    modules = {}
    current_module = None

    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        module_match = re.match(r"Module\s+([IVX]+)", line, re.IGNORECASE)
        if module_match:
            current_module = f"Module {module_match.group(1)}"
            modules[current_module] = []
            continue

        if line.lower().startswith((
            "course outcome",
            "references",
            "textbook",
            "syllabus",
            "marks"
        )):
            continue

        if current_module and len(line) > 5:
            modules[current_module].append(line)

    return modules


# -------------------------------------------------
# TEXTBOOK PARSING & CHUNKING
# -------------------------------------------------
def chunk_text(text, chunk_size=150):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk.strip()) > 50:
            chunks.append(chunk)

    return chunks


# -------------------------------------------------
# STREAMLIT UI
# -------------------------------------------------
st.set_page_config(
    page_title="Question Paper Generation System",
    layout="centered"
)

st.title("📄 Question Paper Generation System")

# =================================================
# SYLLABUS SECTION
# =================================================
st.header("1️⃣ Syllabus Upload & Topic Extraction")

syllabus_file = st.file_uploader(
    "Upload Syllabus PDF",
    type=["pdf"],
    key="syllabus"
)

if syllabus_file:
    st.success("Syllabus uploaded successfully")

    syllabus_text = extract_text_from_pdf(syllabus_file)

    st.subheader("Extracted Syllabus Text (Preview)")
    st.text(syllabus_text[:1000])

    module_topics = extract_module_topics(syllabus_text)

    if module_topics:
        # 🔹 BULLET VIEW
        st.subheader("📘 Module-wise Syllabus Topics (List View)")
        for module, topics in module_topics.items():
            st.markdown(f"### 🔹 {module}")
            for t in topics:
                st.write(f"- {t}")

        # 🔹 TABLE VIEW (THIS IS WHAT YOU WANTED)
        table_data = []
        for module, topics in module_topics.items():
            for topic in topics:
                table_data.append({
                    "Module": module,
                    "Topic": topic
                })

        df_topics = pd.DataFrame(table_data)

        st.subheader("📊 Extracted Syllabus Topics (Table View)")
        st.table(df_topics)

        # Save outputs
        df_topics.to_csv("processed_data/syllabus_topics_table.csv", index=False)
        with open("processed_data/module_wise_topics.json", "w", encoding="utf-8") as f:
            json.dump(module_topics, f, indent=2)

        st.success("Syllabus topics saved successfully")

    else:
        st.warning("No modules detected in syllabus")

# =================================================
# TEXTBOOK SECTION
# =================================================
st.markdown("---")
st.header("2️⃣ Textbook Parsing & Chunking")

textbook_file = st.file_uploader(
    "Upload Textbook PDF",
    type=["pdf"],
    key="textbook"
)

if textbook_file:
    st.success("Textbook uploaded successfully")

    textbook_text = extract_text_from_pdf(textbook_file)

    st.subheader("Extracted Text (Preview)")
    st.text(textbook_text[:1000])

    if st.button("Parse & Chunk Textbook"):
        chunks = chunk_text(textbook_text)

        st.success(f"Total chunks created: {len(chunks)}")

        for i, ch in enumerate(chunks[:3]):
            st.markdown(f"**Chunk {i+1}:**")
            st.write(ch)

        with open("processed_data/textbook_chunks.json", "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2)

        st.success("Chunks saved to processed_data/textbook_chunks.json")
