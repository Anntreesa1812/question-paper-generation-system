import fitz
import os

def extract_images_from_pdf(uploaded_file, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    pdf_bytes = uploaded_file.file.read()
    uploaded_file.file.seek(0)

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images_metadata = []

    for page_index, page in enumerate(doc, start=1):
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            image_name = f"page_{page_index}_img_{img_index+1}.{image_ext}"
            image_path = os.path.join(output_dir, image_name)

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            images_metadata.append({
                "image_id": image_name,
                "page": page_index,        # ✅ METADATA
                "path": image_path
            })

    return images_metadata
