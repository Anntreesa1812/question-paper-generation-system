from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json

# Load data
with open("structured_syllabus.json") as f:
    syllabus = json.load(f)

with open("chunks.json") as f:
    chunks = json.load(f)

chunk_texts = [c["text"] for c in chunks]

module_names = list(syllabus["modules"].keys())
module_texts = [
    syllabus["modules"][m]["raw_text"]
    for m in module_names
]


def evaluate_model(model_path):

    print(f"\nLoading model: {model_path}")
    model = SentenceTransformer(model_path)

    module_emb = model.encode(module_texts, normalize_embeddings=True)
    chunk_emb = model.encode(chunk_texts, normalize_embeddings=True)

    gaps = []

    for emb in chunk_emb:
        sims = cosine_similarity([emb], module_emb)[0]
        sorted_sims = sorted(sims, reverse=True)

        if len(sorted_sims) > 1:
            gap = sorted_sims[0] - sorted_sims[1]
            gaps.append(gap)

    avg_gap = sum(gaps) / len(gaps)
    print("Average separation gap:", round(avg_gap, 4))


# ===========================
# RUN BOTH MODELS
# ===========================



# If your fine-tuned model is extracted in folder:

evaluate_model("sbert_model")