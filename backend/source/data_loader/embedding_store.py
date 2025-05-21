import os
import json
import faiss
from sentence_transformers import SentenceTransformer

# --- Config ---
VECTOR_STORE_PATH = "C:/Users/hp/OneDrive/Desktop/test_here/backend/vector_store/"
MODEL_NAME = "multi-qa-MiniLM-L6-cos-v1"
embedding_model = SentenceTransformer(MODEL_NAME)

def build_vector_store(documents, embedding_model):
    """
    Builds a FAISS vector store from LangChain Document objects.
    """
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

    # Extract text and metadata from LangChain Document objects
    texts = [doc.page_content for doc in documents]
    metadata = [doc.metadata for doc in documents]

    # Ensure each chunk has 'source' metadata
    for meta in metadata:
        meta.setdefault("source", "unknown")

    chunk_dicts = [{"page_content": text, "metadata": meta} for text, meta in zip(texts, metadata)]

    # Embed the text
    embeddings = embedding_model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    faiss.normalize_L2(embeddings)

    # Create FAISS index and store
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, os.path.join(VECTOR_STORE_PATH, "vector.index"))

    # Save chunks with metadata to JSON
    with open(os.path.join(VECTOR_STORE_PATH, "chunks.json"), "w", encoding="utf-8") as f:
        json.dump(chunk_dicts, f, ensure_ascii=False, indent=2)

def load_vector_store():
    """
    Loads the FAISS index and associated chunks from disk.
    """
    index = faiss.read_index(os.path.join(VECTOR_STORE_PATH, "vector.index"))
    with open(os.path.join(VECTOR_STORE_PATH, "chunks.json"), "r", encoding="utf-8") as f:
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
