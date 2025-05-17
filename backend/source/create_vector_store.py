# backend/source/create_vector_store.py

import os
import faiss
import json
from sentence_transformers import SentenceTransformer
from data_loader.preprocessing import preprocess_pdf

# Config
DOCS_PATH = "data/Onboarding.pdf"
VECTOR_STORE_PATH = "backend/vector_store"
os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

# Load PDF and chunk it
chunks = preprocess_pdf(DOCS_PATH)
for chunk in chunks:
    if 'embedding' in chunk:
        chunk['embedding'] = chunk['embedding'].tolist()

# Embed using SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(chunks, show_progress_bar=True)

# Create and save FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

faiss.write_index(index, os.path.join(VECTOR_STORE_PATH, "vector.index"))

# Save chunks metadata for search responses as JSON
with open(os.path.join(VECTOR_STORE_PATH, "chunks.json"), "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)


print("Vector store created successfully.")
