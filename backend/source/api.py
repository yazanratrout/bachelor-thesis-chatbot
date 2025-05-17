from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from source.data_loader.embedding_store import load_vector_store, embedding_model
import faiss

app = FastAPI()

origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # can be restricted to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
index, chunks = load_vector_store()

@app.get("/search")
def search(query: str, top_k: int = 5):
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_embedding, top_k)
    results = [chunks[i] for i in I[0]]
    return {"results": results}
