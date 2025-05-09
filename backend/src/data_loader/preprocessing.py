import os
import logging
import fitz
import nltk
nltk.download("punkt_tab")
from nltk.tokenize import sent_tokenize

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_logger = logging.StreamHandler()
console_logger.setLevel(logging.ERROR)
file_logger = logging.FileHandler("C://Users//yratrout//bachelor-thesis-chatbot-template//bachelor-thesis-chatbot//backend//src//data_loader//preprocessing.log", mode='w')
file_logger.setLevel(logging.INFO)
logging.basicConfig(
    format='[%(levelname)s] %(message)s',
    handlers=[console_logger, file_logger]
)

def load_pdf(file_path):
    if not os.path.exists(file_path):
        logger.error(f"File {file_path} does not exist")
        raise FileNotFoundError(f"File {file_path} does not exist")

    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
        text += "\n"
    doc.close()

    cleaned_text = text.replace("\n\n", "\n").strip()
    return cleaned_text

def chunk_text(text, sentences_per_chunk=3):
    sentences = sent_tokenize(text)
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk = " ".join(sentences[i:i + sentences_per_chunk])
        chunks.append(chunk)
    return chunks

def preprocess_pdf(file_path, sentences_per_chunk=3):
    logger.info(f"Loading PDF: {file_path}")
    text = load_pdf(file_path)
    logger.info(f"Text loaded with length of: {len(text)} characters")

    logger.info("Chunking text")
    chunks = chunk_text(text, sentences_per_chunk)
    logger.info(f"Generated {len(chunks)} chunks")

    return chunks

if __name__ == "__main__":
    path = "backend/documents/onboarding.pdf"
    chunks = preprocess_pdf(path, sentences_per_chunk=3)
    print("\nFirst chunk preview:")
    print(chunks[0])
