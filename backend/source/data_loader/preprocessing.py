import os
import logging
import fitz
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

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

def chunk_text(text, chunk_size=600, chunk_overlap=150):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    texts = splitter.split_text(text)
    documents = [Document(page_content=t) for t in texts]
    return documents

def preprocess_pdf(file_path, chunk_size=700, chunk_overlap=150):
    text = load_pdf(file_path)
    chunks = chunk_text(text, chunk_size, chunk_overlap)
    logger.info(f"Chunked into {len(chunks)} chunks")
    return chunks

# For local testing
if __name__ == "__main__":
    pdf_path = "data/onboarding.pdf"
    chunks = preprocess_pdf(pdf_path)
    print(f"\nFirst chunk:\n{chunks[0]}")