from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from syllabus import extract_text_from_pdf as extract_syllabus_text, extract_module_topics
from chunking import extract_text_from_pdf as extract_textbook_text, chunk_text


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

from fastapi import UploadFile, File
import fitz
import json

from fastapi import UploadFile, File

@app.post("/chunk-textbook")
async def chunk_textbook(file: UploadFile = File(...)):
    text = extract_textbook_text(file)
    chunks = chunk_text(text)

    return {
        "total_chunks": len(chunks),
        "chunks": chunks[:10]  # return first 10 only
    }


