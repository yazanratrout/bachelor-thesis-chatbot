from sentence_transformers import CrossEncoder

reranker_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank_chunks(query: str, chunks: list[str], top_n: int = 1) -> list[str]:
    """
    Re-rank a list of candidate chunks using a CrossEncoder reranker.
    Returns top-N most relevant chunks.
    """
    if not chunks:
        return []

    pairs = [(query, chunk) for chunk in chunks]
    scores = reranker_model.predict(pairs)
    ranked = sorted(zip(scores, chunks), reverse=True)
    return [chunk for _, chunk in ranked[:top_n]]
