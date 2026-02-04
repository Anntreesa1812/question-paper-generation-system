# -------------------------------
# TEXT CHUNKING ONLY
# -------------------------------

def chunk_text_by_page(pages_text, chunk_size=200):
    """
    pages_text = list of tuples -> [(page_number, page_text), ...]
    """
    chunks = []
    chunk_id = 1

    for page_number, text in pages_text:
        words = text.split()

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])

            if len(chunk.strip()) > 50:
                chunks.append({
                    "chunk_id": chunk_id,
                    "page": page_number,     # ✅ METADATA
                    "text": chunk
                })
                chunk_id += 1

    return chunks

