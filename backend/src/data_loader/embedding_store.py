from preprocessing import preprocess_pdf
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_logger = logging.StreamHandler()
console_logger.setLevel(logging.ERROR)
file_logger = logging.FileHandler("C://Users//yratrout//bachelor-thesis-chatbot-template//bachelor-thesis-chatbot//backend//src//data_loader//embedding_store.log", mode='w')
file_logger.setLevel(logging.INFO)
logging.basicConfig(
    format='[%(levelname)s] %(message)s',
    handlers=[console_logger, file_logger]
)

model_name = "sentence-transformers/all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(model_name)
VECTOR_STORE_PATH = "backend/vector_store/"
os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

def build_vector_store(chunks):
    logger.info("Embedding chunks")
    embeddings = embedding_model.encode(chunks, convert_to_numpy=True)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    faiss.write_index(index, os.path.join(VECTOR_STORE_PATH, "vector.index"))

    with open(os.path.join(VECTOR_STORE_PATH, "chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)

def load_vector_store():
    index = faiss.read_index(os.path.join(VECTOR_STORE_PATH, "vector.index"))
    with open(os.path.join(VECTOR_STORE_PATH, "chunks.pkl"), "rb") as f:
        chunks = pickle.load(f)
    return index, chunks

def search(query, top_k=5):
    index, chunks = load_vector_store()
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_embedding, top_k)

    results = [chunks[i] for i in I[0]]
    return results

if __name__ == "__main__":
    pdf_path = "backend/documents/onboarding.pdf"
    chunks = preprocess_pdf(pdf_path)
    build_vector_store(chunks)
    query = "what's the first thing I should do when I move to Munich?"
    top_chunks = search(query)
    print("\nTop matching chunks:")
    for idx, chunk in enumerate(top_chunks):
        print(f"\nChunk {idx+1}:")
        print(chunk)
