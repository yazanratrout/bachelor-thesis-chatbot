import re
import os
import faiss
from .source.data_loader.embedding_store import load_vector_store
from sentence_transformers import SentenceTransformer
from .reranker import rerank_chunks

# Load the FAISS index and corresponding chunks
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_STORE_ROOT = os.path.join(BASE_DIR, "vector_store")

MODEL_REGISTRY = {
    "all-MiniLM-L6-v2": {
        "hf_id": "sentence-transformers/all-MiniLM-L6-v2",
        "store_dir": "vector_store_miniLM",
    },
    "multi-qa-MiniLM-L6-cos-v1": {
        "hf_id": "sentence-transformers/multi-qa-MiniLM-L6-cos-v1",
        "store_dir": "vector_store_multiQA",
    },
    "all-mpnet-base-v2": {
        "hf_id": "sentence-transformers/all-mpnet-base-v2",
        "store_dir": "vector_store_mpnet",
    },
    "paraphrase-MiniLM-L6-v2": {
        "hf_id": "sentence-transformers/paraphrase-MiniLM-L6-v2",
        "store_dir": "vector_store_paraphrase",
    },
}

# Active pipeline (mutates via set_active_model)
_ACTIVE = {
    "model_key": None,
    "embedding_model": None,
    "index": None,
    "chunks": None,
}

def set_active_model(model_key: str):
    """
    Load embedding model + FAISS index/chunks for the given model_key.
    Safe to call multiple times (e.g., when user changes the dropdown).
    """
    if model_key not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model_key '{model_key}'. Choose from {list(MODEL_REGISTRY.keys())}")

    cfg = MODEL_REGISTRY[model_key]
    store_path = os.path.join(VECTOR_STORE_ROOT, cfg["store_dir"])

    index, chunks = load_vector_store(store_path)
    embedding_model = SentenceTransformer(cfg["hf_id"])

    _ACTIVE["model_key"] = model_key
    _ACTIVE["embedding_model"] = embedding_model
    _ACTIVE["index"] = index
    _ACTIVE["chunks"] = chunks
    return model_key

def get_active_model() -> str:
    return _ACTIVE["model_key"]

# Initialize on import (env var or default)
DEFAULT_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
set_active_model(DEFAULT_MODEL)

def clean_text(text: str) -> str:
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s*\n\s*', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

use_reranker = True
def answer_question(query: str, top_k: int = 1, use_reranker: bool = True) -> str:
    """
    Given a query, return the top-1 most relevant chunk from the vector store
    """
    em = _ACTIVE["embedding_model"]
    index = _ACTIVE["index"]
    chunks = _ACTIVE["chunks"]

    if em is None or index is None or chunks is None:
        set_active_model(DEFAULT_MODEL)
        em = _ACTIVE["embedding_model"]; index = _ACTIVE["index"]; chunks = _ACTIVE["chunks"]

    q = em.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(q)
    D, I = index.search(q, top_k)  # cosine sims in [-1, 1]

    candidates = []
    for rank, idx in enumerate(I[0]):
        if 0 <= idx < len(chunks):
            item = chunks[idx]
            text = item["page_content"] if isinstance(item, dict) else str(item)
            source = item.get("metadata", {}).get("source") if isinstance(item, dict) else None
            score = float(D[0][rank]) if len(D) and len(D[0]) > rank else None
            candidates.append({"text": text, "source": source, "score": score})

    if not candidates:
        return {"text": "No relevant answer found.", "source": None, "score": None}

    if use_reranker:
        # Rerank by text; pick best and keep its original score if found
        reranked_texts = rerank_chunks(query, [c["text"] for c in candidates], top_n=1)
        best_text = reranked_texts[0] if reranked_texts else candidates[0]["text"]
        chosen = next((c for c in candidates if c["text"] == best_text), candidates[0])
        return {"text": clean_text(chosen["text"]), "source": chosen["source"], "score": chosen["score"]}

    # No reranker → top-1 from FAISS
    chosen = candidates[0]
    return {"text": clean_text(chosen["text"]), "source": chosen["source"], "score": chosen["score"]}
