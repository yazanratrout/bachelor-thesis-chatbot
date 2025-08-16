import pandas as pd
import matplotlib.pyplot as plt
import os

# Path to evaluation files
eval_dir = "evaluations//indirect-questions-evaluation"
eval_files = [f for f in os.listdir(eval_dir) if f.startswith("Evaluation_") and f.endswith(".xlsx")]

# Define metrics as (base_col, rerank_col)
metrics = [
    ("Fuzzy Match", "Fuzzy Match (>=85)"),
    ("Fuzzy Score", "Fuzzy Score"),
    ("Semantic Match", "Semantic Match (>=0.8)"),
    ("Semantic Score", "Semantic Score"),
    ("Precision@k", "Precision@k After"),
    ("Recall@k", "Recall@k After"),
    ("Reciprocal Rank (MRR component)", "MRR After")
]

# Initialize containers
metric_labels = [m[0] for m in metrics]
model_names = []
base_metrics = {label: [] for label in metric_labels}
rerank_metrics = {label: [] for label in metric_labels}

# Read and process each file
for file in eval_files:
    model_name = file.replace("Evaluation_", "").replace(".xlsx", "")
    model_names.append(model_name)

    file_path = os.path.join(eval_dir, file)
    df_base = pd.read_excel(file_path)
    df_rerank = pd.read_excel(file_path, sheet_name="Reranker Evaluation")

    for (base_col, rerank_col) in metrics:
        base_val = df_base[base_col].mean() if base_col in df_base else 0
        rerank_val = df_rerank[rerank_col].mean() if rerank_col in df_rerank else 0

        base_metrics[base_col].append(base_val)
        rerank_metrics[base_col].append(rerank_val)

# Plotting function
def plot_model_comparison(metric_dict, title, filename):
    bar_width = 0.1
    x = range(len(model_names))
    color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']

    plt.figure(figsize=(13, 6))

    for idx, (metric, values) in enumerate(metric_dict.items()):
        plt.bar(
            [i + bar_width * idx for i in x],
            values,
            width=bar_width,
            label=metric,
            color=color_palette[idx % len(color_palette)]
        )

    plt.xticks([i + bar_width * 3 for i in x], model_names)
    plt.xlabel("Embedding Models")
    plt.ylabel("Score")
    #plt.title(title)
    plt.ylim(0, 1)
    plt.legend()
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    output_path = os.path.join(eval_dir, filename)
    plt.savefig(output_path)
    plt.close()
    print(f"✅ Saved plot: {output_path}")

# Generate both comparison plots
plot_model_comparison(base_metrics, "Model Performance Comparison (Without Reranker)", "plot_model_comparison_without_reranker_indirect_questions.png")
plot_model_comparison(rerank_metrics, "Model Performance Comparison (With Reranker)", "plot_model_comparison_with_reranker_indirect_questions.png")
