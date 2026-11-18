import argparse
import joblib

from config import MODEL_DIR


def predict_clause(text):

    model_path = (
        MODEL_DIR /
        "clauseiq_multiclass_model.joblib"
    )

    if not model_path.exists():

        raise FileNotFoundError(
            "Model not found. Train the model first."
        )

    bundle = joblib.load(model_path)

    model = bundle["model"]

    # Predicted category
    prediction = model.predict([text])[0]

    # Probability for each category
    probabilities = model.predict_proba([text])[0]

    categories = model.named_steps[
        "classifier"
    ].classes_

    ranked_results = sorted(
        zip(categories, probabilities),
        key=lambda x: x[1],
        reverse=True
    )

    return prediction, ranked_results


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--text",
        type=str,
        help="Legal clause text"
    )

    args = parser.parse_args()

    text = args.text

    if not text:

        text = input(
            "\nEnter a legal clause: "
        ).strip()

    if not text:

        raise ValueError(
            "Clause text cannot be empty."
        )

    prediction, probabilities = predict_clause(text)

    print("\n========== CLAUSEIQ PREDICTION ==========")

    print("\nPredicted Category:", prediction)

    print("\nCategory Probabilities:")

    for category, probability in probabilities:

        print(
            f"{category:25s}: "
            f"{probability * 100:.2f}%"
        )


if __name__ == "__main__":

    main()