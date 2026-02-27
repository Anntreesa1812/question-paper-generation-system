import json
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

print("Starting script...")

with open("D:\\text\\Mapping\\Output_json\\mapping_results.json", "r", encoding="utf-8") as f:
    mapping = json.load(f)

print("Modules found:", list(mapping.keys()))

MODEL_PATH = "t5_finetuned_model"

print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)
print("Model loaded.")

def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()

for module_name in mapping.keys():

    print("\n====================================")
    print("Processing:", module_name)
    print("====================================")

    # Take top 5 chunks for context
    sorted_chunks = sorted(
        mapping[module_name],
        key=lambda x: x["score"],
        reverse=True
    )

    top_chunks = sorted_chunks[:5]

    context = " ".join([clean_text(c["text"]) for c in top_chunks])
    context = context[:2000]

    # 🔴 IMPORTANT: This prompt must match your fine-tuning format
    prompt = f"Generate 5 descriptive questions: {context}"

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    )

    outputs = model.generate(
        **inputs,
        max_length=500,
        num_beams=5,
        early_stopping=True
    )

    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print("\nGenerated Questions:\n")
    print(generated_text)