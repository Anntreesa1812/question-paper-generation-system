import streamlit as st
import fitz  # PyMuPDF
import nltk
import pandas as pd
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords

# Download stopwords (only first run)
nltk.download('stopwords')

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
# SYLLABUS TOPIC EXTRACTION (TF-IDF + FALLBACK)
# -------------------------------------------------
def extract_topics(text, top_n=15):
    lines = text.split("\n")

    cleaned_lines = []
    for line in lines:
        line = line.strip().lower()

        # remove module/unit labels
        line = re.sub(r"(module|unit)\s*\w*", "", line)
        line = re.sub(r"(introduction|overview|course|syllabus)", "", line)

        if 5 < len(line) < 100 and any(c.isalpha() for c in line):
            cleaned_lines.append(line)

    stop_words = stopwords.words('english')

    # ---------- TRY TF-IDF ----------
    try:
        vectorizer = TfidfVectorizer(
            stop_words=stop_words,
            ngram_range=(1, 2),
            max_features=30
        )

        tfidf_matrix = vectorizer.fit_transform(cleaned_lines)
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray().sum(axis=0)

        topic_scores = dict(zip(feature_names, scores))
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)

        if len(sorted_topics) >= 5:
            return sorted_topics[:top_n]

    except Exception:
        pass

    # ---------- FALLBACK: KEYWORD HARVESTING ----------
    keywords = set()
    for line in cleaned_lines:
        for word in line.split():
            if word not in stop_words and len(word) > 4:
                keywords.add(word)

    keywords = list(keywords)[:top_n]

    return [(kw, 0.1) for kw in keywords]


# -------------------------------------------------
# STREAMLIT UI
# -------------------------------------------------
st.set_page_config(
    page_title="Question Paper Generation System",
    layout="centered"
)

st.title("📄 Question Paper Generation System")
st.subheader("Syllabus Topic Extraction using TF-IDF")

uploaded_file = st.file_uploader(
    "Upload Syllabus PDF",
    type=["pdf"]
)

if uploaded_file:
    st.success("Syllabus uploaded successfully")

    syllabus_text = extract_text_from_pdf(uploaded_file)

    st.subheader("Extracted Text (Preview)")
    st.text(syllabus_text[:1000])

    if st.button("Extract Topics"):
        topics = extract_topics(syllabus_text)

        df = pd.DataFrame(topics, columns=["Topic", "Score"])

        st.subheader("📌 Extracted Topics")
        st.table(df)

        df.to_csv("processed_data/syllabus_topics.csv", index=False)
        st.success("Topics saved to processed_data/syllabus_topics.csv")
import json

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


st.markdown("---")
st.subheader("📘 Textbook Ingestion & Chunking")

textbook_file = st.file_uploader(
    "Upload Textbook PDF",
    type=["pdf"],
    key="textbook"
)

if textbook_file:
    st.success("Textbook uploaded successfully")

    textbook_text = extract_text_from_pdf(textbook_file)

    st.subheader("Extracted Text Preview (Textbook)")
    st.text(textbook_text[:1000])

    if st.button("Parse & Chunk Textbook"):
        chunks = chunk_text(textbook_text)

        st.success(f"Total chunks created: {len(chunks)}")

        # Display first few chunks
        for i, ch in enumerate(chunks[:3]):
            st.markdown(f"**Chunk {i+1}:**")
            st.write(ch)

        # Save chunks
        with open("processed_data/textbook_chunks.json", "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2)

        st.success("Chunks saved to processed_data/textbook_chunks.json")
