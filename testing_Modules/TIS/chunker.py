# chunker.py

import json
import re


# ==========================================
# SENTENCE SPLITTER
# ==========================================

def split_sentences(text):

    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)

    return [p.strip() for p in parts if len(p.strip()) > 25]


# ==========================================
# CLEAN + NORMALIZE
# ==========================================

def preprocess(text):

    # Remove page markers
    text = re.sub(r"\[PAGE\s+\d+\]", "", text)

    # Remove headers: "12 / Overview"
    text = re.sub(r"\b\d+\s*/\s*Overview\b", "", text)

    # Remove figures
    text = re.sub(r"Figure\s+\d+.*", "", text, flags=re.S)

    # Remove TOC-like pages
    if len(re.findall(r"\d+\.\d+", text)) > 5:
        return ""

    # Separate number-word merges
    text = re.sub(r"\b(\d+)([A-Za-z])", r"\1. \2", text)

    # Normalize tables (uppercase blocks)
    text = re.sub(r"\n([A-Z ]{6,})\n", r" \1 ", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==========================================
# OVERLAP CHUNKER
# ==========================================

def chunk_text(text, size=350, overlap=50):

    sentences = split_sentences(text)

    chunks = []
    buf = []
    wc = 0


    for s in sentences:

        w = len(s.split())

        buf.append(s)
        wc += w

        if wc >= size:

            chunk = " ".join(buf)
            chunks.append(chunk)

            keep = chunk.split()[-overlap:]

            buf = [" ".join(keep)]
            wc = len(keep)


    if buf:
        chunks.append(" ".join(buf))

    return chunks


# ==========================================
# MAIN
# ==========================================

def main():

    with open("D:\\text\\TIS\\Output\\pages_text.json", encoding="utf-8") as f:
        pages = json.load(f)

    chunks = []
    cid = 1


    for p in sorted(pages, key=int):

        raw = pages[p]

        text = preprocess(raw)

        if len(text) < 400:
            continue

        parts = chunk_text(text)

        for part in parts:

            part = re.sub(r"\s+", " ", part).strip()

            chunks.append({
                "id": cid,
                "page": int(p),
                "text": part
            })

            cid += 1


    with open("D:\\text\\TIS\\Output\\chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)


    print(f">>> Generated {len(chunks)} chunks")


if __name__ == "__main__":
    main()