import pandas as pd
import matplotlib.pyplot as plt
import os


# Path to evaluation files
eval_dir = "evaluations//indirect-questions-evaluation"
eval_files = [f for f in os.listdir(eval_dir) if f.startswith("Evaluation_") and f.endswith(".xlsx")]

# Define metrics
metrics = [
    ("Fuzzy Match", "Fuzzy Match (>=85)"),
    ("Fuzzy Score", "Fuzzy Score"),
    ("Semantic Match", "Semantic Match (>=0.8)"),
    ("Semantic Score", "Semantic Score"),
    ("Precision@k", "Precision@k After"),
    ("Recall@k", "Recall@k After"),
    ("Reciprocal Rank (MRR component)", "MRR After")
]

# Plot for each model
for file in eval_files:
    model_name = file.replace("Evaluation_", "").replace(".xlsx", "")
    file_path = os.path.join(eval_dir, file)

    try:
        df_base = pd.read_excel(file_path)
        df_rerank = pd.read_excel(file_path, sheet_name="Reranker Evaluation")

        values_base = []
        values_rerank = []

        # Fuzzy + Semantic from columns
        for metric_base, metric_rerank in metrics:
            values_base.append(df_base[metric_base].mean())
            values_rerank.append(df_rerank[metric_rerank].mean())

        # Plot
        labels = ["Fuzzy Match", "Fuzzy Score", "Semantic Match", "Semantic Score", "Precision@k", "Recall@k", "MRR"]
        x = range(len(labels))
        width = 0.35

        plt.figure(figsize=(10, 5))
        plt.bar([i - width / 2 for i in x], values_base, width=width, label="Original", color="gray")
        plt.bar([i + width / 2 for i in x], values_rerank, width=width, label="Reranker", color="green")

        plt.xticks(x, labels, rotation=45)
        plt.ylabel("Score")
        #plt.title(f"Performance Comparison for {model_name}")
        plt.ylim(0, 1)
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()

        output_path = os.path.join(eval_dir, f"plot_{model_name}_indirect_questions.png")
        plt.savefig(output_path)
        plt.close()

        print(f"✅ Saved comparison plot: {output_path}")

    except Exception as e:
        print(f"❌ Failed for {file}: {e}")