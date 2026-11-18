
import sys
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CSV_PATH = PROJECT_ROOT / "clauses_final.csv"

RESULTS_DIR = PROJECT_ROOT / "ml" / "evaluation" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Import existing rule-based classifier
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.clause_service import classify_clause


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

CATEGORIES = [
    "Privacy",
    "Financial",
    "Cancellation",
    "Data",
    "Intellectual Property",
    "Contractual",
    "Account",
    "Changes"
]

TEST_SPLIT = "test"


# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

def load_test_data():

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {CSV_PATH}"
        )

    df = pd.read_csv(CSV_PATH)

    required_columns = {
        "id", "text", "label", "split"
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing CSV columns: {missing}"
        )

    df = df[df["split"].astype(str).str.lower() == TEST_SPLIT]
    df = df.dropna(subset=["text", "label"])

    df["text"] = df["text"].astype(str)
    df["label"] = df["label"].astype(str).str.strip()

    df = df[df["label"].isin(CATEGORIES)]

    if df.empty:
        raise ValueError(
            "No eligible test records found."
        )

    return df.reset_index(drop=True)


# --------------------------------------------------
# RULE-BASED PREDICTION
# --------------------------------------------------

def predict_rule_based(text):

    category, risk = classify_clause(text)

    return category, risk


# --------------------------------------------------
# EVALUATION
# --------------------------------------------------

def evaluate():

    print("\n========================================")
    print("RULE-BASED CLAUSEIQ EVALUATION")
    print("========================================")

    df = load_test_data()

    print(f"Test records: {len(df)}")

    actual = []
    predicted = []
    risk_levels = []

    for _, row in df.iterrows():

        category, risk = predict_rule_based(row["text"])

        actual.append(row["label"])
        predicted.append(category)
        risk_levels.append(risk)

    # Accuracy includes General predictions as errors
    accuracy = accuracy_score(actual, predicted)

    # Evaluate the eight defined ClauseIQ categories
    precision = precision_score(
        actual,
        predicted,
        labels=CATEGORIES,
        average="macro",
        zero_division=0
    )

    recall = recall_score(
        actual,
        predicted,
        labels=CATEGORIES,
        average="macro",
        zero_division=0
    )

    macro_f1 = f1_score(
        actual,
        predicted,
        labels=CATEGORIES,
        average="macro",
        zero_division=0
    )

    weighted_f1 = f1_score(
        actual,
        predicted,
        labels=CATEGORIES,
        average="weighted",
        zero_division=0
    )

    report = classification_report(
        actual,
        predicted,
        labels=CATEGORIES,
        target_names=CATEGORIES,
        zero_division=0,
        output_dict=True
    )

    matrix = confusion_matrix(
        actual,
        predicted,
        labels=CATEGORIES
    )

    # --------------------------------------------------
    # SAVE PREDICTIONS
    # --------------------------------------------------

    results = df[["id", "text", "label"]].copy()

    results["predicted_label"] = predicted
    results["risk_level"] = risk_levels

    results["correct"] = (
        results["label"] == results["predicted_label"]
    )

    predictions_path = RESULTS_DIR / "rule_based_predictions.csv"

    results.to_csv(
        predictions_path,
        index=False
    )

    # --------------------------------------------------
    # SAVE METRICS
    # --------------------------------------------------

    metrics = {
        "model": "Rule-based",
        "test_records": len(df),
        "accuracy": float(accuracy),
        "precision_macro": float(precision),
        "recall_macro": float(recall),
        "f1_macro": float(macro_f1),
        "f1_weighted": float(weighted_f1),
        "classification_report": report,
        "confusion_matrix": matrix.tolist(),
        "categories": CATEGORIES
    }

    metrics_path = RESULTS_DIR / "rule_based_metrics.json"

    with open(metrics_path, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=4)

    # --------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------

    print("\n--------------- RESULTS ---------------")

    print(f"Accuracy       : {accuracy:.4f}")
    print(f"Macro Precision: {precision:.4f}")
    print(f"Macro Recall   : {recall:.4f}")
    print(f"Macro F1       : {macro_f1:.4f}")
    print(f"Weighted F1    : {weighted_f1:.4f}")

    print("\nClassification Report:")

    print(
        classification_report(
            actual,
            predicted,
            labels=CATEGORIES,
            target_names=CATEGORIES,
            zero_division=0
        )
    )

    print("\nConfusion Matrix:")
    print(matrix)

    print("\nSaved files:")
    print(predictions_path)
    print(metrics_path)

    print("\nRule-based evaluation completed.")


if __name__ == "__main__":
    evaluate()
