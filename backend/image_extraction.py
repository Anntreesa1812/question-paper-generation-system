import fitz
import os

def extract_images_from_pdf(uploaded_file, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    pdf_bytes = uploaded_file.file.read()
    uploaded_file.file.seek(0)

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    image_count = 0

    for page_index, page in enumerate(doc):
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            image_filename = f"page_{page_index+1}_img_{img_index+1}.{image_ext}"
            image_path = os.path.join(output_dir, image_filename)

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            image_count += 1

    return image_count
