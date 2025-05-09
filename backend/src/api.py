from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from src.data_loader.embedding_store import search

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
def search_endpoint(query: str = Query(..., min_length=1)):
    results = search(query)
    return {"query": query, "results": results}