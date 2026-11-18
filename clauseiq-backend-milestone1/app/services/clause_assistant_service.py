
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
    Answer questions about one selected agreement clause.

    Personalization is included only when the authenticated
    user has explicitly consented.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not clause_text or not clause_text.strip():
        raise ValueError("Clause text cannot be empty.")

    personalization_context = ""

    if user:
        personalization_context = build_personalization_context(user)

    if not personalization_context:
        personalization_context = (
            "No user profile context was supplied."
        )

    prompt = f"""
/no_think

You are ClauseIQ, an agreement understanding assistant.

TASK:
Answer the user's question about the selected agreement clause.

STRICT CLAUSE ACCURACY RULES:
- Use ONLY the supplied clause for contractual claims.
- Do not use other clauses or invent agreement provisions.
- Do not assume restrictions that are not explicitly stated.
- Preserve the original meaning of the clause.
- If the answer cannot be established from this clause,
  clearly explain that the information is not available
  in the selected clause.
- Do not provide definitive legal advice.
- Do not declare the clause legally valid or invalid.

PERSONALIZATION RULES:
- Use profile information only when relevant.
- Explain how the clause may relate to the user's
  occupation, age, income or location when appropriate.
- Personal information must never change the meaning
  of the clause.
- Never invent contractual restrictions based on
  the user's profile.
- Do not unnecessarily repeat personal information.
- If no profile context is supplied, simply answer
  without mentioning missing personalization.

OUTPUT RULES:
- Return ONLY the final user-facing answer.
- Never reveal internal reasoning or thought processes.
- Do not narrate your analysis.
- Do not write phrases such as "Let's analyze" or
  "We are given the question".
- Start with a direct answer.
- Explain the clause in simple language.
- Include personal relevance when applicable.
- End with a practical conclusion.
- Be concise and clear.

USER PROFILE CONTEXT:
{personalization_context}

SELECTED CLAUSE:

Section: {section}

Title: {title}

Clause Text:
{clause_text}

USER QUESTION:
{question}

Provide the final answer now.
"""

    answer = generate_response(
        prompt,
        temperature=0.1,
    )

    if not answer or not answer.strip():
        raise ValueError(
            "Ollama returned an empty answer."
        )

    return answer.strip()
