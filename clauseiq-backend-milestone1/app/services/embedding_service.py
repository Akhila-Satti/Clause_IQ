from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIMENSION = 384


model = SentenceTransformer(EMBEDDING_MODEL)


def generate_embedding(text: str) -> list[float]:
    """
    Generate a local semantic embedding for the supplied text.
    """

    if not text or not text.strip():
        raise ValueError(
            "Cannot generate embedding for empty text."
        )

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()