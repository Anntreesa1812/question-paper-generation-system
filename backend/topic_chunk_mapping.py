from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load SBERT model once
model = SentenceTransformer("all-MiniLM-L6-v2")


def map_topics_to_chunks(topics, chunks, top_k=3):
    """
    topics: list[str]
    chunks: list[dict] -> {"chunk_id": int, "text": str}
    """

    topic_texts = topics
    chunk_texts = [chunk["text"] for chunk in chunks]

    # Generate embeddings
    topic_embeddings = model.encode(topic_texts)
    chunk_embeddings = model.encode(chunk_texts)

    # Compute cosine similarity
    similarity_matrix = cosine_similarity(topic_embeddings, chunk_embeddings)

    mapping = {}

    for i, topic in enumerate(topics):
        scores = similarity_matrix[i]
        top_indices = scores.argsort()[-top_k:][::-1]

        mapping[topic] = [
            {
                "chunk_id": chunks[idx]["chunk_id"],
                "score": float(scores[idx])
            }
            for idx in top_indices
        ]

    return mapping
