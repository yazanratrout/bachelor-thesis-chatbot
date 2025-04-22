from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .chatbot import answer_query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ask")
def ask(query: str):
    answer = answer_query(query)
    return {"answer": answer}
