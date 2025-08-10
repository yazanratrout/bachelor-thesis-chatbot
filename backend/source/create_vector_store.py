import os
import json
import faiss
from sentence_transformers import SentenceTransformer
from data_loader.preprocessing import preprocess_pdfs

# --- Config ---
DOCS_DIR = "data"
VECTOR_STORE_PATH = "backend/vector_store"

def create_vector_store(model_name, output_dir=VECTOR_STORE_PATH):
    os.makedirs(output_dir, exist_ok=True)

    print(f"Loading and preprocessing all PDFs in: data")
    pdf_files = [os.path.join(DOCS_DIR, f) for f in os.listdir(DOCS_DIR) if f.lower().endswith(".pdf")]

    if not pdf_files:
        raise FileNotFoundError("No PDF files found in the data directory!")

    documents = preprocess_pdfs(pdf_files)

    texts = [doc.page_content for doc in documents]
    metadata = [doc.metadata for doc in documents]
    chunk_dicts = [{"page_content": text, "metadata": meta} for text, meta in zip(texts, metadata)]

    print(f"Embedding with model: {model_name}")
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

    print("Building FAISS index...")
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, os.path.join(output_dir, "vector.index"))

    with open(os.path.join(output_dir, "chunks.json"), "w", encoding="utf-8") as f:
        json.dump(chunk_dicts, f, ensure_ascii=False, indent=2)

    print(f"Vector store created at {output_dir}")

if __name__ == "__main__":
    models = {
        "all-MiniLM-L6-v2": os.path.join(VECTOR_STORE_PATH, "vector_store_miniLM"),
        "multi-qa-MiniLM-L6-cos-v1": os.path.join(VECTOR_STORE_PATH, "vector_store_multiQA"),
        "all-mpnet-base-v2": os.path.join(VECTOR_STORE_PATH, "vector_store_mpnet"),
        "paraphrase-MiniLM-L6-v2": os.path.join(VECTOR_STORE_PATH, "vector_store_paraphrase"),
    }

    for model_name, out_dir in models.items():
        print(f"\n=== Creating vector store for model: {model_name} ===")
        create_vector_store(model_name, out_dir)