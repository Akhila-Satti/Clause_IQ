import json
import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score
)
from sklearn.metrics import precision_score, recall_score

from config import (
    MODEL_DIR,
    REPORT_DIR,
    TEXT_COLUMN,
    LABEL_COLUMN,
    CATEGORIES
)

from data_loader import load_dataset, get_splits


def main():

    model_path = (
        MODEL_DIR /
        "clauseiq_multiclass_model.joblib"
    )

    if not model_path.exists():

        raise FileNotFoundError(
            "Model not found. Run train.py first."
        )

    # Load model
    bundle = joblib.load(model_path)

    model = bundle["model"]

    # Load test dataset
    df = load_dataset()

    _, _, test_df = get_splits(df)

    X_test = test_df[TEXT_COLUMN].tolist()

    y_test = test_df[LABEL_COLUMN].tolist()

    # Predictions
    predictions = model.predict(X_test)

    # Metrics
    accuracy = accuracy_score(
        y_test,
        predictions
    )
    precision = precision_score(
        y_test, predictions,
        labels=CATEGORIES,
        average="macro",
        zero_division=0
    )

    recall = recall_score(
        y_test, predictions,
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

    print("\n========== FINAL TEST RESULTS ==========")

    print(f"Accuracy: {accuracy:.4f}")

    print(f"Macro F1: {macro_f1:.4f}")

    print(f"Weighted F1: {weighted_f1:.4f}")

    print("\nClassification Report:\n")

    print(
        classification_report(
            y_test,
            predictions,
            labels=CATEGORIES,
            zero_division=0
        )
    )

    # Confusion matrix
    cm = confusion_matrix(
        y_test,
        predictions,
        labels=CATEGORIES
    )

    cm_df = pd.DataFrame(
        cm,
        index=CATEGORIES,
        columns=CATEGORIES
    )

    # Save reports
    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        REPORT_DIR / "test_metrics.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "accuracy": float(accuracy),
                "macro_f1": float(macro_f1),
                "weighted_f1": float(weighted_f1),
                "classification_report": report,
                "precision_macro": float(precision),
                "recall_macro": float(recall)
            },
            file,
            indent=4
        )

    cm_df.to_csv(
        REPORT_DIR / "confusion_matrix.csv"
    )

    # Save individual predictions
    output = test_df[
        ["id", TEXT_COLUMN, LABEL_COLUMN]
    ].copy()

    output["predicted_label"] = predictions

    output["correct"] = (
        output[LABEL_COLUMN] ==
        output["predicted_label"]
    )

    output.to_csv(
        REPORT_DIR / "test_predictions.csv",
        index=False
    )

    print("\nReports saved successfully!")

    print("Location:", REPORT_DIR)
    

if __name__ == "__main__":

    main()