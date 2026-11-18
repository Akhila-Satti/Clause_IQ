
import sys
import json
import joblib
import pandas as pd

from pathlib import Path
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

# --------------------------------------------------
# PATHS AND IMPORTS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "ml" / "src"

sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    MODEL_DIR,
    REPORT_DIR,
    TEXT_COLUMN,
    LABEL_COLUMN,
    CATEGORIES
)

from data_loader import load_dataset, get_splits

from app.services.clause_service import classify_clause


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

CONFIDENCE_THRESHOLD = 0.60

MODEL_PATH = MODEL_DIR / "clauseiq_multiclass_model.joblib"


# --------------------------------------------------
# HYBRID PREDICTION
# --------------------------------------------------

def hybrid_predict(text, model):

    # Get ML prediction and confidence
    ml_prediction = model.predict([text])[0]

    probabilities = model.predict_proba([text])[0]

    confidence = float(max(probabilities))

    # Get rule-based prediction
    rule_prediction, risk_level = classify_clause(text)

    final_prediction = ml_prediction
    method = "ML"

    # Use rule-based prediction only when:
    # 1. ML confidence is below threshold
    # 2. Rule prediction belongs to our eight categories

    if (
        confidence < CONFIDENCE_THRESHOLD
        and rule_prediction in CATEGORIES
    ):
        final_prediction = rule_prediction
        method = "Rule-based override"

    return {
        "ml_prediction": ml_prediction,
        "ml_confidence": confidence,
        "rule_prediction": rule_prediction,
        "risk_level": risk_level,
        "final_prediction": final_prediction,
        "method": method
    }


# --------------------------------------------------
# MAIN EVALUATION
# --------------------------------------------------

def main():

    print("\n======================================")
    print("CLAUSEIQ HYBRID MODEL EVALUATION")
    print("======================================")

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    # Load trained model
    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]

    # Load same test split used by ML evaluation
    df = load_dataset()

    _, _, test_df = get_splits(df)

    test_df = test_df.copy()

    X_test = test_df[TEXT_COLUMN].tolist()
    y_test = test_df[LABEL_COLUMN].tolist()

    print(f"Test records: {len(test_df)}")

    # Generate hybrid predictions
    outputs = []

    for text in X_test:

        result = hybrid_predict(text, model)

        outputs.append(result)

    predictions = [
        item["final_prediction"]
        for item in outputs
    ]

    # --------------------------------------------------
    # METRICS
    # --------------------------------------------------

    accuracy = accuracy_score(
        y_test, predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        labels=CATEGORIES,
        average="macro",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        labels=CATEGORIES,
        average="macro",
        zero_division=0
    )

    macro_f1 = f1_score(
        y_test,
        predictions,
        labels=CATEGORIES,
        average="macro",
        zero_division=0
    )

    weighted_f1 = f1_score(
        y_test,
        predictions,
        labels=CATEGORIES,
        average="weighted",
        zero_division=0
    )

    report = classification_report(
        y_test,
        predictions,
        labels=CATEGORIES,
        output_dict=True,
        zero_division=0
    )

    cm = confusion_matrix(
        y_test,
        predictions,
        labels=CATEGORIES
    )

    # --------------------------------------------------
    # SAVE PREDICTIONS
    # --------------------------------------------------

    output = test_df[
        ["id", TEXT_COLUMN, LABEL_COLUMN]
    ].copy()

    output["ml_prediction"] = [
        item["ml_prediction"] for item in outputs
    ]

    output["ml_confidence"] = [
        item["ml_confidence"] for item in outputs
    ]

    output["rule_prediction"] = [
        item["rule_prediction"] for item in outputs
    ]

    output["risk_level"] = [
        item["risk_level"] for item in outputs
    ]

    output["predicted_label"] = predictions

    output["method"] = [
        item["method"] for item in outputs
    ]

    output["correct"] = (
        output[LABEL_COLUMN] == output["predicted_label"]
    )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    output.to_csv(
        REPORT_DIR / "hybrid_predictions.csv",
        index=False
    )

    # --------------------------------------------------
    # SAVE METRICS
    # --------------------------------------------------

    metrics = {
        "model": "Hybrid",
        "test_records": len(test_df),
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "accuracy": float(accuracy),
        "precision_macro": float(precision),
        "recall_macro": float(recall),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "categories": CATEGORIES,
        "rule_overrides": sum(
            item["method"] == "Rule-based override"
            for item in outputs
        )
    }

    with open(
        REPORT_DIR / "hybrid_metrics.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(metrics, file, indent=4)

    pd.DataFrame(
        cm,
        index=CATEGORIES,
        columns=CATEGORIES
    ).to_csv(
        REPORT_DIR / "hybrid_confusion_matrix.csv"
    )

    # --------------------------------------------------
    # DISPLAY
    # --------------------------------------------------

    print("\n========== HYBRID RESULTS ==========")

    print(f"Accuracy        : {accuracy:.4f}")
    print(f"Macro Precision : {precision:.4f}")
    print(f"Macro Recall    : {recall:.4f}")
    print(f"Macro F1        : {macro_f1:.4f}")
    print(f"Weighted F1     : {weighted_f1:.4f}")

    print(
        "\nRule-based overrides:",
        metrics["rule_overrides"]
    )

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            predictions,
            labels=CATEGORIES,
            zero_division=0
        )
    )

    print("\nSaved reports to:", REPORT_DIR)


if __name__ == "__main__":
    main()
