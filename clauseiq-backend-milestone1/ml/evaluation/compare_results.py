
import json
import pandas as pd

from pathlib import Path


# --------------------------------------------------
# PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ML_REPORT_DIR = PROJECT_ROOT / "ml" / "reports"

RULE_REPORT_DIR = (
    PROJECT_ROOT / "ml" / "evaluation" /"results"
)


# --------------------------------------------------
# LOAD METRICS
# --------------------------------------------------

def load_metrics(directory, filename):

    path = directory / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Missing evaluation report: {path}\n"
            "Run the corresponding evaluation script first."
        )

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


# --------------------------------------------------
# COMPARISON
# --------------------------------------------------

def main():

    print("\n======================================")
    print("CLAUSEIQ MODEL COMPARISON")
    print("======================================")

    rule = load_metrics(
        RULE_REPORT_DIR,
        "rule_based_metrics.json"
    )

    ml = load_metrics(
        ML_REPORT_DIR,
        "test_metrics.json"
    )

    hybrid = load_metrics(
        ML_REPORT_DIR,
        "hybrid_metrics.json"
    )

    models = {
        "Rule-based": rule,
        "ML-based": ml,
        "Hybrid": hybrid
    }

    rows = []

    for model_name, metrics in models.items():

        rows.append({
            "Model": model_name,
            "Accuracy": metrics.get("accuracy", 0),

            "Precision": metrics.get(
                "precision_macro",
                metrics.get("macro_precision", 0)
            ),

            "Recall": metrics.get(
                "recall_macro",
                metrics.get("macro_recall", 0)
            ),

            "Macro F1": metrics.get("macro_f1", 0),

            "Weighted F1": metrics.get("weighted_f1", 0)
        })

    comparison = pd.DataFrame(rows)

    # --------------------------------------------------
    # DISPLAY
    # --------------------------------------------------

    print("\n========== FINAL COMPARISON ==========\n")

    print(
        comparison.to_string(
            index=False,
            formatters={
                "Accuracy": "{:.4f}".format,
                "Precision": "{:.4f}".format,
                "Recall": "{:.4f}".format,
                "Macro F1": "{:.4f}".format,
                "Weighted F1": "{:.4f}".format
            }
        )
    )

    # --------------------------------------------------
    # BEST MODEL
    # --------------------------------------------------

    best_index = comparison["Macro F1"].idxmax()

    best_model = comparison.loc[best_index, "Model"]

    print("\nBest model based on Macro F1:", best_model)

    # --------------------------------------------------
    # SAVE COMPARISON
    # --------------------------------------------------

    ML_REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = ML_REPORT_DIR / "final_comparison.csv"

    comparison.to_csv(
        output_path,
        index=False
    )

    print("\nComparison saved to:", output_path)


if __name__ == "__main__":
    main()
