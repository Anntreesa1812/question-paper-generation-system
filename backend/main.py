import os
import json
import sys
import shutil
# --------------------------------------------------
# ADD BACKEND DIRECTORY TO PATH
# --------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

# --------------------------------------------------
# IMPORTS (AFTER REFACTOR)
# --------------------------------------------------

# Ingestion (PDF + OCR)
from ingestion import extract_text_by_page
# Syllabus processing
from syllabus import (
    extract_text_from_pdf as extract_syllabus_text,
    extract_module_topics
)

# Text chunking
from chunking import chunk_text_by_page
# Semantic mapping
from topic_chunk_mapping import map_topics_to_chunks

# Question pattern & generation
from pattern.pattern_model import ExamPattern
from pattern.pattern_controller import process_exam_pattern
from question_generator import generate_questions_from_pattern
from image_extraction import extract_images_from_pdf
from page_image_mapper import map_chunks_to_images

# --------------------------------------------------
# BASE PATH SETUP
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "processed_data")

os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)


# --------------------------------------------------
# FASTAPI APP
# --------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# TEST ROUTE
# --------------------------------------------------
@app.get("/")
def root():
    return {"status": "Backend running successfully"}


# --------------------------------------------------
# STEP 1: SYLLABUS EXTRACTION
# --------------------------------------------------
@app.post("/extract-syllabus")
async def extract_syllabus(file: UploadFile = File(...)):
    text = extract_syllabus_text(file)
    modules = extract_module_topics(text)

    syllabus_path = os.path.join(PROCESSED_DATA_DIR, "syllabus_topics.json")
    with open(syllabus_path, "w", encoding="utf-8") as f:
        json.dump(modules, f, indent=4)

    return {
        "message": "Syllabus topics extracted successfully",
        "modules": modules
    }


# --------------------------------------------------
# STEP 2: TEXTBOOK INGESTION + CHUNKING
# --------------------------------------------------


@app.post("/chunk-textbook")
def chunk_textbook(file: UploadFile = File(...)):
    import shutil

    # --------------------------------------------------
    # CLEAR OLD IMAGES (OPTION 2)
    # --------------------------------------------------
    image_dir = os.path.join(PROCESSED_DATA_DIR, "images")

    if os.path.exists(image_dir):
        shutil.rmtree(image_dir)

    os.makedirs(image_dir, exist_ok=True)

    # --------------------------------------------------
    # READ PDF ONCE
    # --------------------------------------------------
    pdf_bytes = file.file.read()
    file.file.seek(0)

    # --------------------------------------------------
    # TEXT EXTRACTION WITH PAGE METADATA
    # --------------------------------------------------
    pages_text = extract_text_by_page(pdf_bytes)

    # --------------------------------------------------
    # CHUNKING WITH PAGE METADATA
    # --------------------------------------------------
    chunks = chunk_text_by_page(pages_text)

    # --------------------------------------------------
    # IMAGE EXTRACTION (PAGE METADATA INCLUDED)
    # --------------------------------------------------
    images = extract_images_from_pdf(file, image_dir)

    # --------------------------------------------------
    # MAP CHUNKS ↔ IMAGES USING PAGE NUMBER
    # --------------------------------------------------
    final_chunks = map_chunks_to_images(chunks, images)

    # --------------------------------------------------
    # SAVE FINAL OUTPUT
    # --------------------------------------------------
    output_path = os.path.join(PROCESSED_DATA_DIR, "textbook_chunks.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_chunks, f, indent=4)

    return {
        "message": "Textbook processed successfully",
        "total_chunks": len(final_chunks),
        "total_images": len(images)
    }

    # ---------------------------------------
    # IMAGE EXTRACTION
    # ---------------------------------------
    image_count = extract_images_from_pdf(file, image_dir)

    return {
        "message": "Textbook processed successfully",
        "total_chunks": len(chunks),
        "images_extracted": image_count
    }


# --------------------------------------------------
# STEP 3: SEMANTIC MAPPING
# --------------------------------------------------
@app.post("/semantic-mapping")
def semantic_mapping():
    syllabus_path = os.path.join(PROCESSED_DATA_DIR, "syllabus_topics.json")
    chunks_path = os.path.join(PROCESSED_DATA_DIR, "textbook_chunks.json")

    if not os.path.exists(syllabus_path):
        return {"error": "Syllabus not processed yet"}

    if not os.path.exists(chunks_path):
        return {"error": "Textbook not processed yet"}

    with open(syllabus_path, "r", encoding="utf-8") as f:
        modules = json.load(f)

    topics = []
    for _, topic_list in modules.items():
        topics.extend(topic_list)

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    mapping = map_topics_to_chunks(topics, chunks)

    mapping_path = os.path.join(PROCESSED_DATA_DIR, "topic_chunk_mapping.json")
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=4)

    return {
        "message": "Semantic mapping completed successfully",
        "mapping": mapping
    }


# --------------------------------------------------
# STEP 4: SET QUESTION PATTERN
# --------------------------------------------------
@app.post("/set-question-pattern")
async def set_question_pattern(pattern: ExamPattern):
    generation_plan = process_exam_pattern(pattern)

    pattern_path = os.path.join(PROCESSED_DATA_DIR, "question_pattern.json")
    with open(pattern_path, "w", encoding="utf-8") as f:
        json.dump(generation_plan, f, indent=4)

    return {
        "message": "Question pattern saved successfully",
        "generation_plan": generation_plan
    }


# --------------------------------------------------
# STEP 5: GENERATE QUESTIONS
# --------------------------------------------------
@app.post("/generate-questions")
async def generate_questions(pattern: ExamPattern):
    generated_questions = generate_questions_from_pattern(
        pattern,
        PROCESSED_DATA_DIR
    )

    questions_path = os.path.join(PROCESSED_DATA_DIR, "generated_questions.json")
    with open(questions_path, "w", encoding="utf-8") as f:
        json.dump(generated_questions, f, indent=4)

    return {
        "message": "Questions generated successfully",
        "questions": generated_questions
    }
