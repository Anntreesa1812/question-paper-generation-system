from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")


def map_topics_to_chunks(
    topics,
    chunks,
    similarity_threshold=0.45,
    diversity_threshold=0.85,
    max_chunks=6,
    fallback_chunks=3
):
    topic_embeddings = model.encode(topics)
    chunk_texts = [c["text"] for c in chunks]
    chunk_embeddings = model.encode(chunk_texts)

    similarity_matrix = cosine_similarity(topic_embeddings, chunk_embeddings)
    mapping = {}

    for i, topic in enumerate(topics):
        topic_key = str(topic).strip()
        scores = similarity_matrix[i]

        # -----------------------------
        # Step 1: threshold filtering
        # -----------------------------
        candidates = [
            (idx, score)
            for idx, score in enumerate(scores)
            if score >= similarity_threshold
        ]

        # -----------------------------
        # FALLBACK CASE
        # -----------------------------
        if not candidates:
            best_idx = scores.argmax()
            mapping[topic_key] = [{
                "chunk_id": chunks[best_idx]["chunk_id"],
                "page": chunks[best_idx].get("page"),
                "score": float(scores[best_idx])
            }]
            continue

        # -----------------------------
        # Step 2: sort by score
        # -----------------------------
        candidates.sort(key=lambda x: x[1], reverse=True)

        selected_indices = []

        for idx, score in candidates:
            if not selected_indices:
                selected_indices.append(idx)
                continue

            # diversity check
            is_diverse = True
            for sel_idx in selected_indices:
                sim = cosine_similarity(
                    [chunk_embeddings[idx]],
                    [chunk_embeddings[sel_idx]]
                )[0][0]

                if sim >= diversity_threshold:
                    is_diverse = False
                    break

            if is_diverse:
                selected_indices.append(idx)

            if len(selected_indices) >= max_chunks:
                break

        mapping[topic_key] = [
            {
                "chunk_id": chunks[idx]["chunk_id"],
                "page": chunks[idx].get("page"),
                "score": float(scores[idx])
            }
            for idx in selected_indices
        ]

    return mapping
