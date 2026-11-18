
from app.models.clause import Clause
from app.services.ollama_service import generate_response


def ask_agreement(
    question: str,
    clauses: list[Clause],
    personalization_context: str = "",
) -> str:

    clause_context = "\n\n".join(
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
    )

    user_context = (
        personalization_context.strip()
        if personalization_context
        else "No user profile context was supplied."
    )

    prompt = f"""
/no_think

You are ClauseIQ, an agreement understanding assistant.

TASK:
Answer the user's question directly using the supplied
agreement clauses.

STRICT RESPONSE RULES:
- Return only the final answer for the user.
- Never reveal internal reasoning or thought processes.
- Never narrate your analysis.
- Never write phrases such as "We are given the question",
  "Let's analyze", or "We must answer".
- Do not repeat the prompt or instructions.
- Do not invent agreement provisions.
- Do not assume restrictions that are not in the clauses.
- Use simple, clear language.
- Be concise but sufficiently informative.
- Do not provide definitive legal advice.

PERSONALIZATION:
- Use the profile only when relevant.
- Relate the agreement to the user's occupation,
  age, income, or location when appropriate.
- Never invent contractual restrictions based on
  personal information.
- If no profile context is supplied, do not claim
  that the user has not consented.
- Do not unnecessarily repeat personal information.

ANSWER STRUCTURE:
1. Direct answer.
2. Relevant clauses and their meaning.
3. Personal relevance, if applicable.
4. Important limitations.
5. Practical conclusion.

USER PROFILE CONTEXT:
{user_context}

RETRIEVED AGREEMENT CLAUSES:
{clause_context}

USER QUESTION:
{question}

Write the final user-facing answer now.
"""

    answer = generate_response(
        prompt,
        temperature=0.1,
    )

    if not answer or not answer.strip():
        raise ValueError("Ollama returned an empty answer.")

    return answer.strip()
