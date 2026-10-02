from app.models.clause import Clause
from app.services.ollama_service import generate_response


def ask_agreement(
    question: str,
    clauses: list[Clause],
) -> str:
    """
    Answer a question using only the retrieved
    relevant clauses.
    """

    clause_context = "\n\n".join(
        [
            f"""
SECTION: {clause.section}
TITLE: {clause.title}
CATEGORY: {clause.category}

CLAUSE TEXT:
{clause.text}

CLAUSE SUMMARY:
{clause.summary or ""}
"""
            for clause in clauses
        ]
    )

    prompt = f"""
You are ClauseIQ, an AI-powered legal agreement
understanding assistant.

Answer the user's question using ONLY the supplied
agreement clauses.

IMPORTANT RULES:

- Use only the supplied clauses.
- Do not invent information.
- Do not assume facts that are not provided.
- If the supplied clauses do not contain enough
  information, clearly say that the available
  clauses do not provide enough information.
- Explain the answer in simple language.
- Preserve the meaning of the original clauses.
- Do not provide definitive legal advice.
- Do not claim that a clause is legally valid or invalid.
- Do not make assumptions about the parties' intentions.

RELEVANT AGREEMENT CLAUSES:

{clause_context}

USER QUESTION:

{question}

ANSWER:
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