from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .data_loader.embedding_store import load_vector_store, embedding_model
import faiss
import re

app = FastAPI()

def clean_text(text: str) -> str:
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s*\n\s*', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = text.strip()
    return text


origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
index, chunks = load_vector_store()

@app.get("/search")
def search(query: str, top_k: int = 5):
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_embedding, top_k)
    results = [
        chunks[i]["page_content"] if isinstance(chunks[i], dict) else chunks[i] 
        for i in I[0]
    ]
    cleaned_results = [clean_text(r) for r in results]
    return {"results": cleaned_results}
