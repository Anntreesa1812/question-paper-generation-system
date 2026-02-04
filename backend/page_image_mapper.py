def map_chunks_to_images(chunks, images):
    image_map = {}

    for img in images:
        image_map.setdefault(img["page"], []).append(img)

    for chunk in chunks:
        chunk["images"] = image_map.get(chunk["page"], [])

    return chunks
