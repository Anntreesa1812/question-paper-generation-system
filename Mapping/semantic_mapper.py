import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# =====================================
# CONFIG
# =====================================

SYLLABUS_FILE = "SIS/syllabus_ready.json"
CHUNKS_FILE = "TIS/chunks.json"
OUTPUT_FILE = "mapping/mapping_results.json"

MODEL_NAME = "all-MiniLM-L6-v2"

TOP_K = 6
SCORE_THRESHOLD = 0.45   # Slightly lower because we filter by module


# =====================================
# DEFINE MODULE PAGE RANGES (EDIT THIS)
# =====================================

MODULE_PAGE_RANGES = {
    "MODULE I": (1, 120),
    "MODULE II": (121, 250),
    "MODULE III": (251, 380),
    "MODULE IV": (381, 600)
}


# =====================================
# LOAD JSON
# =====================================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =====================================
# BUILD QUERY
# =====================================

def build_query(item):

    module = item.get("module", "")
    context = item.get("context", "")
    topic = item.get("topic", item.get("text", ""))

    enriched = f"""
    Module: {module}
    Context: {context}
    Topic: {topic}
    This topic discusses definitions, explanations,
    concepts, working principles, characteristics,
    comparisons, processes, strengths, weaknesses,
    applications, performance metrics and theoretical aspects.
    """

    return enriched.strip()


# =====================================
# FILTER CHUNKS BY MODULE RANGE
# =====================================

def filter_chunks_by_module(chunks, module_name):

    if module_name not in MODULE_PAGE_RANGES:
        return chunks

    start, end = MODULE_PAGE_RANGES[module_name]

    filtered = [
        c for c in chunks
        if c.get("page") is not None and start <= c["page"] <= end
    ]

    return filtered


# =====================================
# FILTER LOW-QUALITY CHUNKS
# =====================================

def filter_chunk_quality(text):

    words = text.split()

    if len(words) < 60:
        return False

    numeric_ratio = sum(c.isdigit() for c in text) / max(len(text), 1)
    if numeric_ratio > 0.20:
        return False

    lower = text.lower()

    if "table of contents" in lower:
        return False

    return True


# =====================================
# MAIN
# =====================================

def main():

    print(">>> Loading data...")
    syllabus = load_json(SYLLABUS_FILE)
    chunks = load_json(CHUNKS_FILE)

    print(">>> Loading SBERT model...")
    model = SentenceTransformer(MODEL_NAME)

    results = []

    print(">>> Processing syllabus topics...")

    for item in syllabus:

        module_name = item.get("module", "")

        # ---- Module-level filtering ----
        module_chunks = filter_chunks_by_module(chunks, module_name)

        if not module_chunks:
            results.append({
                "id": item["id"],
                "module": module_name,
                "topic": item.get("text", ""),
                "matches": []
            })
            continue

        chunk_texts = [c["text"] for c in module_chunks]

        chunk_embeddings = model.encode(
            chunk_texts,
            show_progress_bar=False
        )

        query_text = build_query(item)
        query_embedding = model.encode([query_text])

        scores = cosine_similarity(query_embedding, chunk_embeddings)[0]

        ranked_indices = np.argsort(scores)[::-1][:TOP_K]

        matches = []

        for idx in ranked_indices:

            score = float(scores[idx])

            if score < SCORE_THRESHOLD:
                continue

            chunk = module_chunks[idx]

            if not filter_chunk_quality(chunk["text"]):
                continue

            matches.append({
                "chunk_id": chunk["id"],
                "page": chunk["page"],
                "score": round(score, 4),
                "text": chunk["text"]
            })

        results.append({
            "id": item["id"],
            "module": module_name,
            "topic": item.get("text", ""),
            "matches": matches
        })

    print(">>> Saving results...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(">>> Mapping completed successfully.")


# =====================================
# RUN
# =====================================

if __name__ == "__main__":
    main()