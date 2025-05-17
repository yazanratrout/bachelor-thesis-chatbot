import os
import json
import faiss
from sentence_transformers import SentenceTransformer

VECTOR_STORE_PATH = "C:/Users/hp/OneDrive/Desktop/test_here/backend/vector_store/"
MODEL_NAME = "multi-qa-MiniLM-L6-cos-v1"
embedding_model = SentenceTransformer(MODEL_NAME)

def build_vector_store(chunks, embedding_model):
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    embeddings = embedding_model.encode(chunks, convert_to_numpy=True)
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, os.path.join(VECTOR_STORE_PATH, "vector.index"))
    with open(os.path.join(VECTOR_STORE_PATH, "chunks.json"), "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

def load_vector_store():
    index = faiss.read_index(os.path.join(VECTOR_STORE_PATH, "vector.index"))
    with open(os.path.join(VECTOR_STORE_PATH, "chunks.json"), "r", encoding="utf-8") as f:
        chunks = json.load(f)
    return index, chunks
