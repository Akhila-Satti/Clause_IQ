import json
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    f1_score
)

from config import (
    MODEL_DIR,
    REPORT_DIR,
    TEXT_COLUMN,
    LABEL_COLUMN,
    CATEGORIES,
    RANDOM_STATE
)

from data_loader import load_dataset, get_splits


def build_model(C):

    model = Pipeline([

        (
            "tfidf",

            TfidfVectorizer(

                lowercase=True,

                strip_accents="unicode",

                ngram_range=(1, 2),

                min_df=2,

                max_df=0.98,

                max_features=150000,

                sublinear_tf=True,

                # Preserve legal negations
                stop_words=None,

                dtype="float32"
            )
        ),

        (
            "classifier",

            LogisticRegression(

                C=C,

                max_iter=2000,

                solver="lbfgs",

                class_weight=None,

                random_state=RANDOM_STATE
            )
        )

    ])

    return model


def main():

    # Load dataset
    df = load_dataset()

    train_df, val_df, test_df = get_splits(df)

    X_train = train_df[TEXT_COLUMN].tolist()
    y_train = train_df[LABEL_COLUMN].tolist()

    X_val = val_df[TEXT_COLUMN].tolist()
    y_val = val_df[LABEL_COLUMN].tolist()

    # Hyperparameter candidates
    C_values = [0.5, 1.0, 2.0, 4.0]

    results = []

    print("\nStarting model training...\n")

    for C in C_values:

        print(f"Training with C = {C}")

        model = build_model(C)

        model.fit(X_train, y_train)

        predictions = model.predict(X_val)

        accuracy = accuracy_score(
            y_val,
            predictions
        )

        macro_f1 = f1_score(
            y_val,
            predictions,
            labels=CATEGORIES,
            average="macro",
            zero_division=0
        )

        weighted_f1 = f1_score(
            y_val,
            predictions,
            labels=CATEGORIES,
            average="weighted",
            zero_division=0
        )

        results.append({

            "C": C,

            "accuracy": float(accuracy),

            "macro_f1": float(macro_f1),

            "weighted_f1": float(weighted_f1)

        })

        print(
            f"Accuracy: {accuracy:.4f} | "
            f"Macro F1: {macro_f1:.4f} | "
            f"Weighted F1: {weighted_f1:.4f}\n"
        )

    # Select best model using validation macro F1
    best_result = max(
        results,
        key=lambda x: (
            x["macro_f1"],
            x["accuracy"]
        )
    )

    best_C = best_result["C"]

    print("Best C value:", best_C)

    # Refit using train + validation
    train_val_df = df[
        df["split"].isin(["train", "val"])
    ]

    X_train_val = train_val_df[TEXT_COLUMN].tolist()

    y_train_val = train_val_df[LABEL_COLUMN].tolist()

    final_model = build_model(best_C)

    final_model.fit(
        X_train_val,
        y_train_val
    )

    # Create directories
    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save model
    model_path = (
        MODEL_DIR /
        "clauseiq_multiclass_model.joblib"
    )

    bundle = {

        "model": final_model,

        "categories": CATEGORIES,

        "best_C": best_C,

        "training_rows": len(train_df),

        "validation_rows": len(val_df),

        "final_training_rows": len(train_val_df),

        "model_type": "TF-IDF + Multiclass Logistic Regression"

    }

    joblib.dump(
        bundle,
        model_path
    )

    # Save validation results
    with open(
        REPORT_DIR / "validation_results.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "results": results,
                "best_result": best_result
            },
            file,
            indent=4
        )

    print("\nTraining completed successfully!")

    print("Model saved at:", model_path)

    print("\nRun the evaluation script next.")


if __name__ == "__main__":

    main()