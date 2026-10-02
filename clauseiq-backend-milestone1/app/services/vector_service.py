from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import generate_embedding


def store_document_chunks(
    db: Session,
    document_id: int,
    chunks: list[str],
) -> list[DocumentChunk]:
    """
    Generate embeddings for document chunks and store them
    in PostgreSQL using pgvector.
    """

    chunk_models = []

    for index, content in enumerate(chunks):

        embedding = generate_embedding(content)

        chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=index,
            content=content,
            embedding=embedding,
        )

        db.add(chunk)
        chunk_models.append(chunk)

    db.commit()

    for chunk in chunk_models:
        db.refresh(chunk)

    return chunk_models