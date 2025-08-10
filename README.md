
# 📚 Information Retrieval Chatbot (Bachelor Thesis)

This project is a closed-domain **information retrieval chatbot** that answers questions based on internal PDF documentation using extractive chunk-based semantic search.

Designed for:
- Lightweight, private document QA
- Easy evaluation across multiple embedding models
- Integration of **LLM-as-a-judge** for scoring relevance and correctness

---

## 🚀 Features

- 🔍 **Semantic Search** with Sentence Transformers & FAISS
- 📄 **Chunk-based Retrieval** (no LLM generation)
- ⚙️ **FastAPI Backend**, 🌐 **React Frontend**
- 📊 **Evaluation Tools**: Top-1, Precision@k, MRR, and LLM Judging
- 🧠 Supports multiple embedding models
- 🔐 Works offline / private-doc compliant

---

## 🗂️ Folder Structure

```
bachelor-thesis-chatbot/
├── backend/
│   ├── source/
│   │   ├── api.py
│   │   ├── create_vector_store.py
│   │   └── data_loader/
│   │       ├── embedding_store.py
│   │       └── preprocessing.py
│   ├── vector_store/             # FAISS index + metadata
│   ├── main.py
│   └── requirements.txt
│
├── data/
│   └── *.pdf                    # Documents to embed
│
├── evaluations/
│   ├── evaluate_with_llm_judge.py  # Evaluation via GPT or Together
│   ├── auto_eval.py
│   ├── retrieval_eval.py
│   ├── Retrieval_Chatbot_Evaluation_Template.xlsx
│   ├── Evaluation_*.xlsx       # Evaluation results per model
│   ├── Model_Comparison_Summary.xlsx
│   ├── Model_Performance_Comparison.png
│   └── *_qa.json               # Evaluation question sets
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── Chatbot.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

---

## 🛠️ Getting Started

### 1. ✅ Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
uvicorn source.api:app --reload
```

### 2. ✅ Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## ⚙️ Configuration

You can set `.env` variables to control:
- Model name (e.g. `multi-qa-MiniLM-L6-cos-v1`)
- Embedding paths
- Optional OpenAI / Together API keys for evaluation

---

## 📊 Evaluation System

Supports both automatic and LLM-based evaluation:
- ✅ Top-1 Accuracy
- ✅ Precision@k
- ✅ Recall@k
- ✅ Mean Reciprocal Rank (MRR)
- ✅ Optional Human Ratings
- ✅ LLM-as-a-Judge (GPT-3.5, GPT-4, LLaMA via Together)

📂 Results are stored in:
- `Evaluation_*.xlsx` — per model
- `Model_Comparison_Summary.xlsx` — score overview
- `Model_Performance_Comparison.png` — bar chart

### LLM Evaluation Output
| Query | Retrieved Answer | Reference | Relevance | Correctness | Completeness | Justification |
|-------|------------------|-----------|-----------|-------------|--------------|----------------|

---

## 🔐 Privacy and Security

- All embeddings and documents stay local
- No generation or logging of user queries
- Evaluation with external LLMs (optional) can be toggled
- `.gitignore` includes all raw documents and vector stores

---

## 🧠 Bachelor Thesis Context

This chatbot is the core of a Bachelor's thesis on:
> **"Design and Evaluation of a Lightweight, Private Information Retrieval Chatbot with LLM-based Automated Scoring"**

Goals:
- Avoid full LLM deployment
- Focus on chunk-based retrieval
- Enable automated, scalable evaluation

---

## 📌 Future Improvements

- [ ] Add RAG + LLM generation fallback for unseen queries
- [ ] Streamlit-based leaderboard dashboard
- [ ] Embedding quality visualization

---

## 🧪 Example Embedding Models Tested

- `multi-qa-MiniLM-L6-cos-v1`
- `all-MiniLM-L6-v2`
- `all-mpnet-base-v2`
- `paraphrase-MiniLM-L6-v2`

Each model was evaluated using both retrieval metrics and LLM-based ratings.

---

## 🤝 Credits

Built with:
- [SentenceTransformers](https://www.sbert.net/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)