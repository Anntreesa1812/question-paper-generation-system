from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import json

from syllabus import extract_text_from_pdf as extract_syllabus_text, extract_module_topics
from chunking import extract_text_from_pdf as extract_textbook_text, chunk_text
from topic_chunk_mapping import map_topics_to_chunks


# -------------------------------
# Helper: Load syllabus topics
# -------------------------------
def load_syllabus_topics():
    with open("processed_data/syllabus_topics.json", "r") as f:
        data = json.load(f)

    topics = []
    for module, topic_list in data.items():
        topics.extend(topic_list)

    return topics


app = FastAPI()

# -------------------------------
# CORS (IMPORTANT for React)
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# TEST ROUTE
# -------------------------------
@app.get("/")
def root():
    return {"status": "Backend running"}

# -------------------------------
# SYLLABUS EXTRACTION ROUTE
# -------------------------------
@app.post("/extract-syllabus")
def extract_syllabus(file: UploadFile = File(...)):
    text = extract_syllabus_text(file)
    modules = extract_module_topics(text)
    return modules

# -------------------------------
# TEXTBOOK CHUNKING ROUTE
# -------------------------------
@app.post("/chunk-textbook")
async def chunk_textbook(file: UploadFile = File(...)):
    text = extract_textbook_text(file)
    chunks = chunk_text(text)

    return {
        "total_chunks": len(chunks),
        "chunks": chunks[:10]
    }

# -------------------------------
# SEMANTIC MAPPING ROUTE ✅
# -------------------------------
@app.post("/semantic-mapping")
def semantic_mapping(file: UploadFile = File(...)):
    # 1️⃣ Extract textbook text
    text = extract_textbook_text(file)

    # 2️⃣ Chunk textbook
    raw_chunks = chunk_text(text)
    chunks = [
        {"chunk_id": i + 1, "text": c}
        for i, c in enumerate(raw_chunks)
    ]

    # 3️⃣ Load syllabus topics (dynamic)
    topics = load_syllabus_topics()

    # 4️⃣ Semantic mapping (SBERT)
    mapping = map_topics_to_chunks(topics, chunks)

    return mapping
