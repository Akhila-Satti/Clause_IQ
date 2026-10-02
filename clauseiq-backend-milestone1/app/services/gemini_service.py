import json

from google import genai

from app.core.config import settings
from app.services.ollama_service import generate_json_response


# Gemini is temporarily retained only for embeddings.
# We will replace this separately after the local LLM migration.
client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)



def analyze_document(text: str) -> dict:
    """
    Analyze a legal document using the local Ollama model.

    Gemini is no longer used for document generation.
    """

    prompt = f"""
You are ClauseIQ, an AI-powered legal document analysis assistant.

Your task is to analyze the provided legal document and return
STRUCTURED JSON ONLY.

IMPORTANT:
- Do not provide definitive legal advice.
- The analysis is informational only.
- Do not claim that a clause is legally valid or invalid.
- Base your analysis only on the provided document.
- Do not invent clauses, obligations, or facts that are not present.
- If something is unclear or missing, say so.
- Preserve the meaning of the original document.

Return JSON with EXACTLY this structure:

{{
  "summary": "A concise plain-language overview of the document.",
  "clauses": [
    {{
      "section": "Section or clause number if available",
      "title": "Short descriptive title",
      "category": "Privacy | Financial | Cancellation | Data | Intellectual Property | Contractual | Account | Changes | General",
      "summary": "Explain what this clause means in simple language.",
      "risk_level": "LOW | MEDIUM | HIGH | CRITICAL",
      "risks": [
        "Potential issue or point the user should pay attention to."
      ],
      "obligations": [
        "Important obligation created by this clause."
      ]
    }}
  ],
  "recommendations": [
    "General points the user may want to review carefully."
  ]
}}

Risk levels are ATTENTION INDICATORS for informational purposes.
They are NOT legal validity determinations.

Only include clauses that are actually supported by the document.

LEGAL DOCUMENT:
{text}
"""

    raw_text = generate_json_response(
        prompt,
        temperature=0.1,
    )

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Ollama returned invalid JSON: {exc}"
        ) from exc

    if not isinstance(result, dict):
        raise ValueError(
            "Ollama response must be a JSON object."
        )

    result.setdefault("summary", "")
    result.setdefault("clauses", [])
    result.setdefault("recommendations", [])

    return result


def analyze_clauses(clauses: list[dict]) -> dict:
    """
    Analyze already-segmented clauses using Ollama.

    Clause segmentation remains ClauseIQ's own responsibility.
    """

    clause_text = "\n\n".join(
        [
            f"""
CLAUSE INDEX: {index}
SECTION: {clause.get("section", "")}
TITLE: {clause.get("title", "")}
TEXT:
{clause.get("text", "")}
"""
            for index, clause in enumerate(clauses, start=1)
        ]
    )

    prompt = f"""
You are ClauseIQ, an AI-powered legal document analysis assistant.

Analyze the clauses provided below.

IMPORTANT:
- Do NOT create new clauses.
- Do NOT remove clauses.
- Preserve the clause index.
- Analyze only the supplied text.
- Do not invent facts.
- Do not provide definitive legal advice.
- Risk levels are informational attention indicators,
  NOT legal validity determinations.

Return JSON ONLY using exactly this structure:

{{
  "summary": "A concise overview of the supplied clauses.",
  "clauses": [
    {{
      "index": 1,
      "summary": "Simple-language explanation of the clause.",
      "risk_level": "LOW | MEDIUM | HIGH | CRITICAL",
      "risks": [
        "Potential issue the user should pay attention to."
      ],
      "obligations": [
        "Important obligation created by this clause."
      ]
    }}
  ],
  "recommendations": [
    "Important points the user should review."
  ]
}}

There must be exactly one result for every supplied clause.

SUPPLIED CLAUSES:

{clause_text}
"""

    raw_text = generate_json_response(
        prompt,
        temperature=0.1,
    )

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Ollama returned invalid JSON: {exc}"
        ) from exc

    if not isinstance(result, dict):
        raise ValueError(
            "Ollama response must be a JSON object."
        )

    result.setdefault("summary", "")
    result.setdefault("clauses", [])
    result.setdefault("recommendations", [])

    return result


