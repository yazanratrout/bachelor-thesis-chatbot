import os
from sentence_transformers import SentenceTransformer
from source.data_loader.embedding_store import build_vector_store, load_vector_store
from source.data_loader.preprocessing import preprocess_pdf
import faiss

VECTOR_STORE_PATH = "C:/Users/hp/OneDrive/Desktop/test_here/backend/vector_store/"

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
PDF_FILE_PATH = "data/onboarding.pdf"

chunks = preprocess_pdf(PDF_FILE_PATH)

print("Building vector store...")
build_vector_store(chunks, embedding_model)
print("Vector store created and saved.\n")

# Step 2: Load vector store
print("Loading vector store...")
index, loaded_chunks = load_vector_store()
print(f"Loaded {len(loaded_chunks)} chunks.\n")

# Step 3: Perform semantic search
query = "what should I in case I lost the access chip?"
query_embedding = embedding_model.encode([query], convert_to_numpy=True)
faiss.normalize_L2(query_embedding)

# Search top 3 results
k = 3
D, I = index.search(query_embedding, k)

print("Top matching chunks:")
for rank, idx in enumerate(I[0]):
    print(f"{rank + 1}. {loaded_chunks[idx]}")
