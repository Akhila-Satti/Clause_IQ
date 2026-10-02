from app.services.ollama_service import generate_response


def ask_about_clause(
    question: str,
    section: str,
    title: str,
    clause_text: str,
) -> str:
    """
    Answer the user's question using only the supplied clause.
    """

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