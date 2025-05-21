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

def chunk_text(text, chunk_size=700, chunk_overlap=150):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    texts = splitter.split_text(text)
    documents = [Document(page_content=t) for t in texts]
    return documents

def preprocess_pdfs(file_paths, chunk_size=700, chunk_overlap=150):
    all_chunks = []
    for path in file_paths:
        text = load_pdf(path)
        chunks = chunk_text(text, chunk_size, chunk_overlap)
        for chunk in chunks:
            chunk.metadata["source"] = os.path.basename(path)
        all_chunks.extend(chunks)
        logger.info(f"Chunked '{path}' into {len(chunks)} chunks")
    return all_chunks

# For local testing
if __name__ == "__main__":
    pdfs_folder = "data"
    pdf_files = [os.path.join(pdfs_folder, f) for f in os.listdir(pdfs_folder) if f.endswith(".pdf")]
    
    if not pdf_files:
        logger.warning("No PDF files found in the 'data' folder.")
    else:
        chunks = preprocess_pdfs(pdf_files)
        print(f"\nFirst chunk:\n{chunks[0]}")
