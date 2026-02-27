import json
import os
import re
from transformers import T5ForConditionalGeneration, T5Tokenizer


# ============================
# CONFIG
# ============================

MAPPING_FILE = "D:\\text\\Mapping\\Output_json\\mapping_results.json"
SYLLABUS_FILE = "D:\\text\\SIS\\Output_Json\\structured_syllabus.json"
MODEL_NAME = "google/flan-t5-large"   # use large if your system allows
TOP_K = 10
MAX_CONTEXT_CHARS = 2500


# ============================
# LOAD DATA
# ============================

if not os.path.exists(MAPPING_FILE):
    print("❌ mapping_results.json not found.")
    exit()

with open(MAPPING_FILE, "r", encoding="utf-8") as f:
    mapping = json.load(f)

with open(SYLLABUS_FILE, "r", encoding="utf-8") as f:
    syllabus_data = json.load(f)


# ============================
# LOAD MODEL
# ============================

print("Loading model...")
tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ============================
# GENERATE 5 QUESTIONS PER MODULE
# ============================

for module_name in mapping.keys():

    print("\n========================================")
    print(f"MODULE: {module_name}")
    print("========================================\n")

    sorted_chunks = sorted(
        mapping[module_name],
        key=lambda x: x["score"],
        reverse=True
    )

    top_chunks = sorted_chunks[:TOP_K]

    module_raw = syllabus_data["modules"][module_name]["raw_text"]

    context = module_raw + " " + " ".join(
        [clean_text(chunk["text"]) for chunk in top_chunks]
    )

    context = context[:MAX_CONTEXT_CHARS]

    prompt = f"""
You are preparing a university end-semester examination.

Generate exactly 5 descriptive theory questions for each module.

Rules:
- Each question must begin with Explain, Discuss, Analyze, Compare, Evaluate, or Derive.
- Each question must be suitable for 8–10 marks.
- Do NOT generate multiple-choice questions.
- Do NOT use phrases like "Which of the following".
- Questions must require conceptual understanding.

Module Content:
{context}
"""

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    )

    outputs = model.generate(
        **inputs,
        max_length=500,
        num_beams=5,
        early_stopping=True
    )

    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print(generated_text)
    print("\n")