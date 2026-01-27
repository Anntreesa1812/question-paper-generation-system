import os
import json
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from syllabus import extract_text_from_pdf as extract_syllabus_text, extract_module_topics
from chunking import extract_text_from_pdf as extract_textbook_text, chunk_text
from topic_chunk_mapping import map_topics_to_chunks
from pattern.pattern_model import ExamPattern, QuestionPattern
from pattern.pattern_controller import process_exam_pattern
from question_generator import generate_questions_from_pattern



# --------------------------------------------------
# BASE PATH SETUP (VERY IMPORTANT)
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "processed_data")

# Ensure processed_data folder exists
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)


# --------------------------------------------------
# FASTAPI APP
# --------------------------------------------------
app = FastAPI()

# Add CORS middleware BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# --------------------------------------------------
# TEST ROUTE
# --------------------------------------------------
@app.get("/")
def root():
    return {"status": "Backend running"}


# --------------------------------------------------
# STEP 1: SYLLABUS EXTRACTION
# --------------------------------------------------
@app.post("/extract-syllabus")
def extract_syllabus(file: UploadFile = File(...)):
    text = extract_syllabus_text(file)
    modules = extract_module_topics(text)

    syllabus_path = os.path.join(PROCESSED_DATA_DIR, "syllabus_topics.json")
    with open(syllabus_path, "w", encoding="utf-8") as f:
        json.dump(modules, f, indent=4)

    return {
        "message": "Syllabus topics extracted and stored",
        "modules": modules
    }


# --------------------------------------------------
# STEP 2: TEXTBOOK CHUNKING
# --------------------------------------------------
@app.post("/chunk-textbook")
async def chunk_textbook(file: UploadFile = File(...)):
    text = extract_textbook_text(file)
    raw_chunks = chunk_text(text)

    chunks = [
        {"chunk_id": i + 1, "text": chunk}
        for i, chunk in enumerate(raw_chunks)
    ]

    chunks_path = os.path.join(PROCESSED_DATA_DIR, "textbook_chunks.json")
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4)

    return {
        "message": "Textbook chunked and stored",
        "total_chunks": len(chunks)
    }


# --------------------------------------------------
# STEP 3: SEMANTIC MAPPING (NO FILE UPLOAD)
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
    for module, topic_list in modules.items():
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

@app.post("/set-question-pattern")
async def set_question_pattern(pattern: ExamPattern):
    try:
        generation_plan = process_exam_pattern(pattern)

        pattern_path = os.path.join(PROCESSED_DATA_DIR, "question_pattern.json")
        with open(pattern_path, "w", encoding="utf-8") as f:
            json.dump(generation_plan, f, indent=4)

        return {
            "message": "Question pattern saved successfully",
            "generation_plan": generation_plan
        }
    except Exception as e:
        return {
            "error": f"Failed to save question pattern: {str(e)}"
        }, 400

@app.post("/generate-questions")
async def generate_questions(pattern: ExamPattern):
    try:
        # Generate questions based on pattern and available resources
        generated_questions = generate_questions_from_pattern(pattern, PROCESSED_DATA_DIR)
        
        # Save generated questions
        questions_path = os.path.join(PROCESSED_DATA_DIR, "generated_questions.json")
        with open(questions_path, "w", encoding="utf-8") as f:
            json.dump(generated_questions, f, indent=4)
        
        return {
            "message": "Questions generated successfully",
            "questions": generated_questions
        }
    
    except Exception as e:
        return {
            "error": f"Failed to generate questions: {str(e)}"
        }, 400
