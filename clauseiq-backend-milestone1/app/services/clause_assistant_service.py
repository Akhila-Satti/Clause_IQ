from app.models.user import User
from app.services.ollama_service import generate_response
from app.services.personalization_service import (
    build_personalization_context,
)


def ask_about_clause(
    question: str,
    section: str,
    title: str,
    clause_text: str,
    user: User | None = None,
) -> str:
    """
    Answer the user's question using only the supplied clause.

    Optional personalization is included only when the
    authenticated user has given consent.
    """

    personalization_context = ""

    if user:
        personalization_context = (
            build_personalization_context(user)
        )

    prompt = f"""
You are ClauseIQ, an AI-powered legal agreement
understanding assistant.

Answer the user's question using ONLY the supplied clause.

IMPORTANT:
- Do not invent information.
- Do not use information outside the supplied clause.
- Do not provide definitive legal advice.
- Do not claim that the clause is legally valid or invalid.
- If the clause does not contain enough information to answer,
  clearly say that the information is not available in this clause.
- Explain the answer in simple language.
- Preserve the meaning of the original clause.
- Do not make assumptions about the parties' intentions.
- Personalization must never override the supplied clause.

{personalization_context}

CLAUSE:

Section:
{section}

Title:
{title}

Text:
{clause_text}

USER QUESTION:
{question}

Provide a concise, easy-to-understand answer.
"""

    answer = generate_response(
        prompt,
        temperature=0.2,
    )

    if not answer:
        raise ValueError(
            "Ollama returned an empty answer."
        )

    return answer