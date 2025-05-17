import fitz  # PyMuPDF
import re

def preprocess_pdf(file_path, chunk_size=100):
    doc = fitz.open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    # Clean and split text
    sentences = re.split(r'(?<=[.!?]) +', full_text)
    chunks = [
        " ".join(sentences[i:i + chunk_size])
        for i in range(0, len(sentences), chunk_size)
    ]
    return chunks
