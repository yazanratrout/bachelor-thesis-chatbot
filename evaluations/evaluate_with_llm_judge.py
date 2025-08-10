from together import Together
import pandas as pd
import time
import json
import re
import os
from dotenv import load_dotenv
load_dotenv()

os.environ["TOGETHER_API_KEY"] = os.getenv("TOGETHER_API_KEY")
client = Together()

excel_files = [
    "evaluations/direct-questions-evaluation/Evaluation_all-MiniLM-L6-v2_direct_questions.xlsx",
    "evaluations/direct-questions-evaluation/Evaluation_all-mpnet-base-v2_direct_questions.xlsx",
    "evaluations/direct-questions-evaluation/Evaluation_multi-qa-MiniLM-L6-cos-v1_direct_questions.xlsx",
    "evaluations/direct-questions-evaluation/Evaluation_paraphrase-MiniLM-L6-v2_direct_questions.xlsx"
]

def evaluate_with_llm(df, query_col, retrieved_col, reference_col, extra_cols=None):
    eval_data = []
    for idx, row in df.iterrows():
        query = str(row.get(query_col, ""))
        retrieved = str(row.get(retrieved_col, ""))
        reference = str(row.get(reference_col, ""))

        if not query or not retrieved or not reference:
            continue

        prompt = f"""
        You are a helpful evaluator for a question-answering system.
        Evaluate how well the retrieved answer matches the user's question and the gold reference answer.
        Rate the retrieved answer (0 to 5) on the following:
        - Relevance: How related is the answer to the question?
        - Correctness: Is the answer factually accurate based on the reference?
        - Completeness: Does it fully answer the question?
        Also provide a one-sentence justification.
        Question: {query}
        Retrieved Answer:
        \"\"\"{retrieved}\"\"\"
        Reference Answer:
        \"\"\"{reference}\"\"\"
        Respond with this JSON format:
        {{
        "relevance": [0-5],
        "correctness": [0-5],
        "completeness": [0-5],
        "justification": "your one-sentence explanation"
        }}
        """

        try:
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                messages=[
                    {"role": "system", "content": "You are a careful evaluator of answer quality."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            content = response.choices[0].message.content
            match = re.search(r'{.*}', content, re.DOTALL)
            row_data = {
                "User Query": query,
                "Retrieved Answer": retrieved,
                "Reference Answer": reference,
            }

            if match:
                scores = json.loads(match.group(0))
                row_data.update({
                    "LLM_Relevance": scores.get("relevance", ""),
                    "LLM_Correctness": scores.get("correctness", ""),
                    "LLM_Completeness": scores.get("completeness", ""),
                    "LLM_Justification": scores.get("justification", "").strip()
                })
            else:
                row_data.update({
                    "LLM_Relevance": "",
                    "LLM_Correctness": "",
                    "LLM_Completeness": "",
                    "LLM_Justification": content.strip()
                })

            # Add additional columns if specified
            if extra_cols:
                for col in extra_cols:
                    row_data[col] = row.get(col, "")

            eval_data.append(row_data)
            time.sleep(1.5)

        except Exception as e:
            print(f"❌ Error at row {idx}: {e}")
            continue

    return pd.DataFrame(eval_data)

# Process all files
for file in excel_files:
    print(f"\nEvaluating file: {file}")
    sheets = pd.read_excel(file, sheet_name=None)
    df_main = sheets.get("Sheet1")
    if df_main is None:
        df_main = list(sheets.values())[0]
    df_rerank = sheets.get("Reranker Evaluation")

    print("Evaluating original top-1 answers...")
    eval_df_1 = evaluate_with_llm(df_main, "User Query",
                                  "Top-1 Retrieved Chunk",
                                  "Gold Standard Chunk Text",
                                  extra_cols=["Precision@k", "Recall@k", "Reciprocal Rank (MRR component)"])

    if df_rerank is not None and "Reranked Top-1" in df_rerank.columns:
        print("Evaluating reranked top-1 answers...")
        eval_df_2 = evaluate_with_llm(
        df_rerank,
        "Query",
        "Reranked Top-1",
        "Gold Standard",
        extra_cols=["Precision@k After", "Recall@k After", "MRR After"]
    )
    else:
        print("❌ Reranked Top-1 sheet or column not found. Skipping reranker evaluation.")
        eval_df_2 = pd.DataFrame()

    # Save both to separate sheets
    with pd.ExcelWriter(file, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
        eval_df_1.to_excel(writer, sheet_name="LLM_eval_without_reranker", index=False)
        if not eval_df_2.empty:
            eval_df_2.to_excel(writer, sheet_name="LLM_eval_with_reranker", index=False)

    print(f"✅ Evaluation saved to: {file}")
