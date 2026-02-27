import json
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# ==============================
# CONFIG
# ==============================

SYLLABUS_FILE = "D:\\text\\SIS\\Output_Json\\structured_syllabus.json"
TEXTBOOK_FILE = "D:\\text\\TIS\\Output\\chunks.json"
OUTPUT_FILE = "D:\\text\\Mapping\\Output_json\\mapping_results.json"
SIMILARITY_THRESHOLD = 0.45
MODEL_NAME = "sbert_model"   # Change if needed


# ==============================
# LOAD JSON
# ==============================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ==============================
# NORMALIZE TEXTBOOK STRUCTURE
# ==============================

def extract_chunks(textbook_data):
    """
    Ensures we always return:
    [
        {"id": ..., "text": ...},
        ...
    ]
    """

    # Case 1: Already a list
    if isinstance(textbook_data, list):
        return textbook_data

    # Case 2: Dict with known keys
    if isinstance(textbook_data, dict):

        if "pages" in textbook_data:
            return textbook_data["pages"]

        if "chunks" in textbook_data:
            return textbook_data["chunks"]

    raise ValueError("❌ Unknown textbook JSON structure.")


# ==============================
# SBERT MAPPER
# ==============================

class ModuleMapper:

    def __init__(self, model_name=MODEL_NAME):
        print(">>> Loading SBERT model...")
        self.model = SentenceTransformer(model_name)

    def embed(self, texts):
        return self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

    def map_chunks(self, textbook_data, syllabus_modules, threshold=0.45):

        if not syllabus_modules:
            raise ValueError("❌ No modules found in syllabus.")

        module_names = list(syllabus_modules.keys())

        # Embed module-level combined text
        module_texts = [
            syllabus_modules[m]["embedding_ready_text"]
            for m in module_names
        ]

        print(">>> Embedding modules...")
        module_embeddings = self.embed(module_texts)

        # Extract chunk texts safely
        chunk_texts = []
        chunk_ids = []

        for item in textbook_data:
            if "text" not in item:
                continue
            chunk_texts.append(item["text"])
            chunk_ids.append(item.get("id", None))

        if not chunk_texts:
            raise ValueError("❌ No valid chunk texts found.")

        print(">>> Embedding textbook chunks...")
        chunk_embeddings = self.embed(chunk_texts)

        results = {m: [] for m in module_names}

        print(">>> Computing similarities...")

        for i, chunk_emb in enumerate(chunk_embeddings):

            sims = cosine_similarity(
                [chunk_emb],
                module_embeddings
            )[0]

            best_idx = np.argmax(sims)
            best_score = float(sims[best_idx])

            if best_score >= threshold:
                results[module_names[best_idx]].append({
                    "chunk_id": chunk_ids[i],
                    "text": chunk_texts[i],
                    "score": round(best_score, 4)
                })

        return results


# ==============================
# MAIN
# ==============================

def main():

    print(">>> Current working directory:", os.getcwd())

    if not os.path.exists(SYLLABUS_FILE):
        print("❌ Syllabus file not found:", SYLLABUS_FILE)
        return

    if not os.path.exists(TEXTBOOK_FILE):
        print("❌ Textbook JSON not found:", TEXTBOOK_FILE)
        return

    print(">>> Loading syllabus...")
    syllabus = load_json(SYLLABUS_FILE)

    if "modules" not in syllabus:
        raise ValueError("❌ 'modules' key not found in syllabus JSON.")

    print(">>> Loading textbook JSON...")
    textbook_raw = load_json(TEXTBOOK_FILE)

    # Normalize structure
    textbook_data = extract_chunks(textbook_raw)

    mapper = ModuleMapper()

    print(">>> Running mapping...")
    mapping = mapper.map_chunks(
        textbook_data,
        syllabus["modules"],
        threshold=SIMILARITY_THRESHOLD
    )

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    print(">>> Saving results...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    print("\n===== MAPPING SUMMARY =====")

    for module, items in mapping.items():
        print(f"{module}: {len(items)} chunks mapped")

    print("\n>>> Mapping complete.")
    print(">>> Output saved to", OUTPUT_FILE)


if __name__ == "__main__":
    main()