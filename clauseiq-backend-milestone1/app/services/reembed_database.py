from app.core.database import SessionLocal
from app.models.clause import Clause
from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import generate_embedding


def reembed_database():
    db = SessionLocal()

    try:
        clauses = db.query(Clause).all()

        print(f"Found {len(clauses)} clauses.")

        for index, clause in enumerate(clauses, start=1):

            text = " ".join(
                [
                    clause.section or "",
                    clause.title or "",
                    clause.text or "",
                    clause.summary or "",
                ]
            ).strip()

            if not text:
                continue

            clause.embedding = generate_embedding(text)

            print(
                f"Embedded clause {index}/{len(clauses)}"
            )

        chunks = db.query(DocumentChunk).all()

        print(f"Found {len(chunks)} document chunks.")

        for index, chunk in enumerate(chunks, start=1):

            if not chunk.content or not chunk.content.strip():
                continue

            chunk.embedding = generate_embedding(
                chunk.content
            )

            print(
                f"Embedded chunk {index}/{len(chunks)}"
            )

        db.commit()

        print()
        print("================================")
        print("RE-EMBEDDING COMPLETE")
        print("================================")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    reembed_database()