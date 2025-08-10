import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from ast import literal_eval
from sentence_transformers import SentenceTransformer, util
from backend.source.data_loader.embedding_store import load_vector_store, search_query
from backend.reranker import rerank_chunks
from rapidfuzz import fuzz


# Define models and vector store directories
VECTOR_STORE_PATH = "backend/vector_store"
models = {
    "all-MiniLM-L6-v2": os.path.join(VECTOR_STORE_PATH, "vector_store_miniLM"),
    "multi-qa-MiniLM-L6-cos-v1": os.path.join(VECTOR_STORE_PATH, "vector_store_multiQA"),
    "all-mpnet-base-v2": os.path.join(VECTOR_STORE_PATH, "vector_store_mpnet"),
    "paraphrase-MiniLM-L6-v2": os.path.join(VECTOR_STORE_PATH, "vector_store_paraphrase"),
}

def fuzzy_match(gold, retrieved, threshold=85):
    ratio = fuzz.token_set_ratio(gold, retrieved)
    return ratio >= threshold, ratio

def semantic_match(gold, retrieved, model, threshold=0.8):
    embeddings = model.encode([gold, retrieved], convert_to_tensor=True)
    cosine_score = util.cos_sim(embeddings[0], embeddings[1]).item()
    return cosine_score >= threshold, cosine_score

summary_rows = []
for model_name, store_path in models.items():
    print(f"\nEvaluating model: {model_name}")
    embedding_model = SentenceTransformer(model_name)
    index, chunks = load_vector_store(store_path)

    df = pd.read_excel(os.path.join(os.path.dirname(__file__), "Retrieval_Chatbot_Evaluation_Template_direct_questions.xlsx"))
    top1_results = []

    for i, row in df.iterrows():
        query = str(row["User Query"])
        results = search_query(query, index, chunks, embedding_model, k=5)
        top_k_texts = [r["page_content"] for r in results]

        top1 = top_k_texts[0] if top_k_texts else ""
        df.at[i, "Top-1 Retrieved Chunk"] = top1
        df.at[i, "Top-k Retrieved Chunks"] = str(top_k_texts)
        gold = str(row["Gold Standard Chunk Text"])
        relevant_chunks = []
        for chunk in top_k_texts:
            similarity = 0
            _, similarity = semantic_match(gold, chunk, embedding_model)
            if similarity >= 0.1:
                relevant_chunks.append(chunk)

        df.at[i, "Number of Relevant Chunks in Top-k"] = str(relevant_chunks)

        gold = str(row["Gold Standard Chunk Text"])
        is_fuzzy, fuzzy_score = fuzzy_match(gold, top1)
        is_semantic, semantic_score = semantic_match(gold, top1, embedding_model)

        top1_results.append({
            "Fuzzy": is_fuzzy,
            "Fuzzy Score": fuzzy_score,
            "Semantic": is_semantic,
            "Semantic Score": semantic_score
        })

    result_df = pd.DataFrame(top1_results)
    df["Fuzzy Match"] = result_df["Fuzzy"]
    df["Fuzzy Score"] = result_df["Fuzzy Score"]
    df["Semantic Match"] = result_df["Semantic"]
    df["Semantic Score"] = result_df["Semantic Score"]

    fuzzy = df["Fuzzy Match"].mean()
    semantic = df["Semantic Match"].mean()

    precision_list, recall_list, rr_list = [], [], []
    for _, row in df.iterrows():
        try:
            top_k_chunks = literal_eval(str(row["Top-k Retrieved Chunks"]))
            relevant_chunks = literal_eval(str(row["Number of Relevant Chunks in Top-k"]))
            precision = len(relevant_chunks) / len(top_k_chunks) if top_k_chunks else 0
            recall = 1.0 if len(relevant_chunks) > 0 else 0
            precision_list.append(precision)
            recall_list.append(recall)

            rr = 0
            for rank, chunk in enumerate(top_k_chunks, start=1):
                if chunk in relevant_chunks:
                    rr = 1 / rank
                    break
            rr_list.append(rr)
        except:
            precision_list.append(0)
            recall_list.append(0)
            rr_list.append(0)

    prec = sum(precision_list) / len(precision_list)
    rec = sum(recall_list) / len(recall_list)
    mrr = sum(rr_list) / len(rr_list)

    df["Precision@k"] = precision_list
    df["Recall@k"] = recall_list
    df["Reciprocal Rank (MRR component)"] = rr_list

    # Save evaluation
    out_file = os.path.join("evaluations//direct-questions-evaluation", f"Evaluation_{model_name.replace('/', '_')}_direct_questions.xlsx")
    df.to_excel(out_file, index=False)
    print(f"Saved model results to: {out_file}")

    # Append to summary
    summary_rows.append({
        "Model": model_name,
        "Top-1 Fuzzy": round(fuzzy, 3),
        "Top-1 Semantic": round(semantic, 3),
        "Precision@k": round(prec, 3),
        "Recall@k": round(rec, 3),
        "MRR": round(mrr, 3)
    })

    # Reranker Evaluation per Model
    reranker_eval = []
    for _, row in df.iterrows():
        query = str(row["User Query"])
        gold = str(row["Gold Standard Chunk Text"])
        try:
            top_k_chunks = literal_eval(str(row["Top-k Retrieved Chunks"]))
        except:
            top_k_chunks = []

        reranked_chunks = rerank_chunks(query, top_k_chunks, top_n=len(top_k_chunks))
        reranked_top1 = reranked_chunks[0] if reranked_chunks else ""

        fuzzy_ok, fuzzy_score = fuzzy_match(gold, reranked_top1)
        sem_ok, sem_score = semantic_match(gold, reranked_top1, embedding_model)

        try:
            original_rank = top_k_chunks.index(reranked_top1) + 1
        except ValueError:
            original_rank = "NotInTopK"

        # Relevant chunks are same logic as before
        relevant_chunks = []
        for chunk in reranked_chunks:
            _, similarity = semantic_match(gold, chunk, embedding_model)
            if similarity >= 0.2:
                relevant_chunks.append(chunk)

        # Compute reranked metrics
        precision_after = len([c for c in reranked_chunks if c in relevant_chunks]) / len(reranked_chunks) if reranked_chunks else 0
        recall_after = 1.0 if any(c in relevant_chunks for c in reranked_chunks) else 0
        mrr_after = next((1 / (i + 1) for i, c in enumerate(reranked_chunks) if c in relevant_chunks), 0)

        reranker_eval.append({
            "Query": query,
            "Gold Standard": gold,
            "Original Top-1": row["Top-1 Retrieved Chunk"],
            "Reranked Top-1": reranked_top1,
            "Original Rank in Top-K": original_rank,
            "Fuzzy Match (>=85)": fuzzy_ok,
            "Fuzzy Score": fuzzy_score,
            "Semantic Match (>=0.8)": sem_ok,
            "Semantic Score": sem_score,
            "Precision@k After": precision_after,
            "Recall@k After": recall_after,
            "MRR After": mrr_after
        })

    reranker_df = pd.DataFrame(reranker_eval)
    with pd.ExcelWriter(out_file, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        reranker_df.to_excel(writer, sheet_name="Reranker Evaluation", index=False)

# Save summary table
summary_df = pd.DataFrame(summary_rows)
summary_df.to_excel(os.path.join("evaluations//direct-questions-evaluation", "Model_Comparison_Summary_direct_questions.xlsx"), index=False)
print("\nAll evaluations completed.")
print("Saved summary to Model_Comparison_Summary.xlsx")