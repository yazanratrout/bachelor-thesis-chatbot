import re
import os
from .source.data_loader.embedding_store import load_vector_store
from sentence_transformers import SentenceTransformer
from .reranker import rerank_chunks

# Load the FAISS index and corresponding chunks
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_STORE_PATH = os.path.join(BASE_DIR, "vector_store", "vector_store_miniLM")

index, chunks = load_vector_store(VECTOR_STORE_PATH)
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def clean_text(text: str) -> str:
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s*\n\s*', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

use_reranker = True
def answer_question(query: str, top_k: int = 1) -> str:
    """
    Given a query, return the top-1 most relevant chunk from the vector store
    """
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_embedding, top_k)

    results = [
        chunks[i]["page_content"] if isinstance(chunks[i], dict) else chunks[i]
        for i in I[0]
    ]
    if use_reranker:
        results = rerank_chunks(query, results, top_n=1)
    return clean_text(results[0]) if results else "No relevant answer found."
