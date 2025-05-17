import os
import logging
import fitz  # PyMuPDF
import nltk
from nltk.tokenize import sent_tokenize

# Optional: download only if not already done
nltk.download("punkt", quiet=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

def load_pdf(file_path):
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File {file_path} does not exist")

    logger.info(f"Reading file: {file_path}")
    doc = fitz.open(file_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    
    cleaned_text = text.replace("\n\n", "\n").strip()
    return cleaned_text

def chunk_text(text, sentences_per_chunk=3):
    sentences = sent_tokenize(text)
    chunks = [" ".join(sentences[i:i + sentences_per_chunk]) for i in range(0, len(sentences), sentences_per_chunk)]
    return chunks

def preprocess_pdf(file_path, sentences_per_chunk=3):
    text = load_pdf(file_path)
    chunks = chunk_text(text, sentences_per_chunk)
    logger.info(f"Chunked into {len(chunks)} chunks")
    return chunks

# For local testing
if __name__ == "__main__":
    pdf_path = "data/onboarding.pdf"
    chunks = preprocess_pdf(pdf_path)
    print(f"\n First chunk:\n{chunks[0]}")
