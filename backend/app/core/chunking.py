import re

def clean_text(text: str):
    text = re.sub(r"<[^>]+>", "", text)  # remove HTML
    text = text.replace("\n\n", "\n")
    return text.strip()

def chunk_text(text: str, max_length=500):
    words = text.split()
    chunks = []
    current = []

    for word in words:
        current.append(word)
        if len(current) >= max_length:
            chunks.append(" ".join(current))
            current = []

    if current:
        chunks.append(" ".join(current))

    return chunks
