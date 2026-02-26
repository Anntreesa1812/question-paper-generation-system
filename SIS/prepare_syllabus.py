import json
import re
import spacy


INPUT_FILE = "syllabus_parsed.json"
OUTPUT_FILE = "syllabus_ready.json"

nlp = spacy.load("en_core_web_sm")


# ------------------------------------
# Utilities
# ------------------------------------

def clean(text):
    return re.sub(r"\s+", " ", text).strip()


def has_capital_nouns(text):
    """
    Detect standalone technical phrases
    like: Palm Print, Gait Recognition
    """
    words = text.split()
    caps = sum(1 for w in words if w[0].isupper())

    return caps >= 2


def is_strong_topic(text):

    doc = nlp(text)

    nouns = 0
    adjs = 0

    for token in doc:
        if token.pos_ in ("NOUN", "PROPN"):
            nouns += 1
        elif token.pos_ == "ADJ":
            adjs += 1

    words = len(text.split())

    # Main rule
    if nouns + adjs >= 2 and words >= 3:
        return True

    # Standalone detection
    if has_capital_nouns(text):
        return True

    # Section-like titles
    if ":" in text:
        return True

    return False


def should_reset_context(topic):

    keywords = [
        "scan", "print", "recognition",
        "biometrics", "system", "technology"
    ]

    t = topic.lower()

    for k in keywords:
        if k in t:
            return True

    return False


# ------------------------------------
# MAIN
# ------------------------------------

def main():

    with open(INPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    output = []
    idx = 1

    current_context = ""


    for module, topics in data.items():

        for topic in topics:

            topic = clean(topic)

            # Decide strength
            strong = is_strong_topic(topic)

            # Reset context if new domain appears
            if strong and should_reset_context(topic):
                current_context = topic
                final_text = topic

            elif strong:
                current_context = topic
                final_text = topic

            else:

                # Weak topic
                if current_context:
                    final_text = f"{topic} in {current_context}"
                else:
                    final_text = topic


            output.append({
                "id": idx,
                "module": module,
                "context": current_context,
                "text": final_text
            })

            idx += 1


    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


    print(f">>> Created {len(output)} entries")


if __name__ == "__main__":
    main()