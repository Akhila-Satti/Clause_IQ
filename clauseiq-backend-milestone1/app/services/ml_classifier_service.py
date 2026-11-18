
from functools import lru_cache
from pathlib import Path

import joblib


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "clauseiq_multiclass_model.joblib"
)


@lru_cache(maxsize=1)
def load_model():
    """
    Load the trained ML model only once.
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained ML model not found: {MODEL_PATH}"
        )

    bundle = joblib.load(MODEL_PATH)

    if "model" not in bundle:
        raise ValueError(
            "Invalid model bundle: 'model' key missing."
        )

    return bundle["model"]


def predict_category(text: str) -> str:
    """
    Predict the clause category using
    TF-IDF + Logistic Regression.
    """

    if not text or not text.strip():
        return "General"

    model = load_model()

    prediction = model.predict([text])[0]

    return str(prediction)


def predict_category_with_confidence(text: str):
    """
    Return predicted category and confidence.
    Useful for debugging and future improvements.
    """

    if not text or not text.strip():
        return "General", 0.0

    model = load_model()

    prediction = model.predict([text])[0]

    probabilities = model.predict_proba([text])[0]

    confidence = float(max(probabilities))

    return str(prediction), confidence
