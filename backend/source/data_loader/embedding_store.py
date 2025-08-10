import os
import json
import faiss

VECTOR_STORE_PATH = "backend/vector_store"

def load_vector_store(store_path=VECTOR_STORE_PATH):
    """
    Loads the FAISS index and associated chunks from disk.
    """
    index_path = os.path.join(store_path, "vector.index")
    chunks_path = os.path.join(store_path, "chunks.json")
    index = faiss.read_index(index_path)
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunk_dicts = json.load(f)
    return index, chunk_dicts

def search_query(query, index, chunks, embedding_model, k=3):
    """
    Performs semantic search over the vector store.
    """
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)
    D, I = index.search(query_embedding, k)
    return [chunks[i] for i in I[0]]
