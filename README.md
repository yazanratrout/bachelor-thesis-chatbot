# Information Retrieval Chatbot (Thesis Project)

A lightweight, **retrieval-based** chatbot that answers questions from an internal corpus of PDFs.
It uses Sentence-Transformers embeddings + FAISS for fast similarity search and (optionally) a cross-encoder **reranker**. A Streamlit UI provides an easy front end for demos.

---

## Features

- **Document ingestion**: PDF parsing and chunking with LangChain splitters
- **Vector search**: FAISS index with **cosine similarity** (via Inner Product on L2-normalized vectors)
- **Multiple embedding models**: switch live in the UI
- **Reranking**: toggle a cross-encoder reranker on/off
- **Evaluation tooling**: templates, auto-eval script(s), and plotting utilities
- **Streamlit UI**: sidebar controls + answer source display (and optional similarity score)

> **First run requires internet** (to download models to cache). Afterwards it works offline using the local cache. Alternatively, you can bundle the Hugging Face model cache for fully offline use.

---

## Repository Structure (key parts)

```
backend/
  ├─ chatbot.py                    # model selection, retrieval, reranker hook
  ├─ reranker.py                   # cross-encoder reranker
  └─ source/
     ├─ create_vector_store.py     # build FAISS indexes for all models
     └─ data_loader/
        ├─ preprocessing.py        # PDF reading + chunking
        └─ embedding_store.py      # load/search vector stores
ui/
  └─ app.py                        # Streamlit chat UI
evaluations/
  ├─ Retrieval_Chatbot_Evaluation_Template_direct_questions.xlsx
  ├─ Retrieval_Chatbot_Evaluation_Template_indirect_questions.xlsx
  ├─ direct-questions-evaluation/  # results + plots
  ├─ indirect-questions-evaluation/# results + plots
  ├─ plot_model_comparison.py
  └─ plot_metrics_comparison.py
data/                               # place your PDFs here
backend/vector_store/               # generated indexes (one subfolder per model)
icons/                              # optional bot avatars for the UI
```

---

## Environment & Requirements

- **Tested with**: Python **3.12** on Windows 11
- Create and activate a virtual environment, then install deps:
  ```bash
  python -m venv venv
  # Windows
  venv\Scripts\activate
  # macOS/Linux
  # source venv/bin/activate

  python -m pip install --upgrade pip
  pip install -r requirements.txt
  ```

### Notes on dependencies

- `sentence-transformers`, `faiss-cpu`, `PyMuPDF`, `numpy`, `streamlit`, `langchain`, `langchain-core`
- `pandas`, `matplotlib`, `rapidfuzz` for evaluation/plots
- `together` only if you use the LLM judge script
- If you append to Excel files in evaluation: **`openpyxl`** is required (already suggested in `requirements.txt` comments)

---

## Model Options (Why these four?)

All four are widely used Sentence-Transformers that balance quality vs. speed/size:

- **all-MiniLM-L6-v2** — small & fast baseline, great latency for demos.
- **multi-qa-MiniLM-L6-cos-v1** — tuned for **question–answer** retrieval; often improves recall for natural questions.
- **all-mpnet-base-v2** — larger & stronger general semantic model; better quality but heavier.
- **paraphrase-MiniLM-L6-v2** — robust on paraphrase/similarity; good fallback for varied phrasing.

Each model gets its own FAISS store under `backend/vector_store/`.

---

## Build Vector Stores (one-time or after changing data/chunking)

> **Requires internet on the first run** to download models. Re-run whenever you add PDFs or change chunking.

From the repo root:
```bash
# Remove old stores if switching similarity settings or chunking
# Windows:
# rmdir /s /q backend\vector_store
# mkdir backend\vector_store
# macOS/Linux:
# rm -rf backend/vector_store && mkdir -p backend/vector_store

# Build all four indexes
python -m backend.source.create_vector_store
```

What this does:
- Parses PDFs in `data/`
- Splits into chunks
- Computes embeddings and **L2-normalizes** them
- Stores them in a FAISS **IndexFlatIP** (so inner product == cosine similarity on unit vectors)
- Writes `vector.index` and `chunks.json` per model

---

## Run the Chatbot UI

You can use the provided `run.bat` on Windows, or run Streamlit manually:

```bash
streamlit run ui/app.py
```

### UI Controls (sidebar)
- **Embedding model**: switch between the four stores live
- **Top-k candidates**: choose how many FAISS hits to consider
- **Use reranker**: on/off (cross-encoder reranks the top-k texts)
- **Show similarity score**: optionally display cosine similarity under answers
- Answers also show the **Source** filename of the retrieved chunk

---

## Retrieval Details (important for the thesis)

- **Cosine similarity** is implemented as **Inner Product** on **L2-normalized** embeddings:
  - Build time: normalize all corpus vectors and store in `IndexFlatIP`
  - Query time: normalize the query vector before searching
  - FAISS distances `D` are cosine similarities in `[-1, 1]`
- This ensures **consistent top-k ordering** across code paths (UI and evaluation scripts).

---

## Evaluation & Plots

1) Prepare your question sets in the `.xlsx` templates under `evaluations/`:
   - `Retrieval_Chatbot_Evaluation_Template_direct_questions.xlsx`
   - `Retrieval_Chatbot_Evaluation_Template_indirect_questions.xlsx`

2) Run the **auto-eval** script(s) (direct/indirect). Example for direct:
   ```bash
   # Example; adjust to your script name/path if different
   python evaluations/auto_eval_direct.py
   ```
   This will produce per-model results in:
   - `evaluations/direct-questions-evaluation/`
   - and write a summary table (Precision@k, Recall@k, MRR, etc.)

3) Generate plots:
   ```bash
   python evaluations/plot_model_comparison.py
   python evaluations/plot_metrics_comparison.py
   ```
   Plots are written alongside the evaluation spreadsheets (direct & indirect folders).

> If you append new sheets to an existing Excel file, make sure **`openpyxl`** is installed.

---

## Secrets & Offline Use

- Create a local `.env`. Example:
  ```dotenv
  # .env.example
  TOGETHER_API_KEY=
  DEBUG=true
  ```
- If you use the LLM judge, set `TOGETHER_API_KEY` locally.
- For **offline** operation, run once online to populate your Hugging Face cache (models will be used from cache afterwards).

---

## Troubleshooting

- **No PDFs found**: ensure your files are in `data/` and have the `.pdf` extension.
- **Index/search mismatch**: if you change chunking or similarity settings, **rebuild** all vector stores.
- **Excel writing errors**: install `openpyxl`.
