import os
import json
import faiss
from sentence_transformers import SentenceTransformer
from data_loader.preprocessing import preprocess_pdfs

# --- Config ---
DOCS_DIR = "data"
VECTOR_STORE_PATH = "backend/vector_store"
MODEL_NAME = "all-MiniLM-L6-v2"
os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

# --- Load and chunk all PDFs ---
print(f"Loading and preprocessing all PDFs in: {DOCS_DIR}")
pdf_files = [os.path.join(DOCS_DIR, f) for f in os.listdir(DOCS_DIR) if f.lower().endswith(".pdf")]

if not pdf_files:
    raise FileNotFoundError("No PDF files found in the data directory!")

documents = preprocess_pdfs(pdf_files)

# --- Extract page content and metadata ---
texts = [doc.page_content for doc in documents]
metadata = [doc.metadata for doc in documents]
chunk_dicts = [{"page_content": text, "metadata": meta} for text, meta in zip(texts, metadata)]

# --- Embedding ---
print("Embedding chunks...")
model = SentenceTransformer(MODEL_NAME)
embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

# --- FAISS Index ---
print("Building FAISS index...")
dimension = embeddings.shape[1]
faiss.normalize_L2(embeddings)
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)
faiss.write_index(index, os.path.join(VECTOR_STORE_PATH, "vector.index"))

# --- Save chunks with metadata ---
with open(os.path.join(VECTOR_STORE_PATH, "chunks.json"), "w", encoding="utf-8") as f:
    json.dump(chunk_dicts, f, ensure_ascii=False, indent=2)

print("Vector store created and saved.")
