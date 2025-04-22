
# Inofrmation Retrieval Chatbot

A closed-domain chatbot that answers questions from internal documentation using:
- Semantic Search (Sentence Transformers + FAISS)
- Extractive Summarization
- Python (FastAPI) backend
- React frontend
- Private document handling

---

## Project Structure

```
backend/
  └── src/
      ├── api.py         # FastAPI endpoints
      ├── chatbot.py     # Orchestrates answering
      ├── config.py      # Env + paths
frontend/
  └── src/
      ├── App.jsx        # Main UI
data/
  ├── docs/              # Raw confidential files
  ├── chunks/            # Preprocessed files
  ├── embeddings/        # FAISS index
```

---

## Getting Started

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.api:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## .env Example
See `.env` for model config and API keys.

---

## Security

- Raw documents and vector stores are excluded from Git
- No data is sent to external APIs unless explicitly configured
