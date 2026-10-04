from app.services.ollama_service import generate_agreement_response


def generate_agreement(
    agreement_type: str,
    parties: str,
    purpose: str,
    location: str,
    duration: str,
    financial_terms: str,
    additional_requirements: str,
) -> str:

    prompt = f"""
You are ClauseIQ's agreement drafting engine.

TASK:
Write the actual draft of the requested agreement.

You are NOT being asked to explain how an agreement should be
written.

You are NOT being asked to analyze the user's information.

You are NOT being asked to discuss your reasoning.

You MUST directly write the agreement.

========================
USER REQUIREMENTS
========================

Agreement Type:
{agreement_type}

Parties:
{parties}

Purpose:
{purpose}

Location:
{location}

Duration:
{duration}

Financial Terms:
{financial_terms}

Additional Requirements:
{additional_requirements}

========================
DRAFTING RULES
========================

1. Output the agreement itself.

2. Do NOT write phrases such as:
   - "The user provided..."
   - "We are creating..."
   - "The user wants..."
   - "Based on the information..."
   - "I will create..."
   - "Let's create..."
   - "The user probably meant..."

3. Do NOT explain your reasoning.

4. Do NOT analyze or discuss the requirements.

5. Do NOT repeat the user's input as a summary.

6. Do NOT invent specific personal information.

7. If a required detail is missing, use a placeholder such as:
   [LANDLORD NAME]
   [TENANT NAME]
   [PROPERTY ADDRESS]
   [START DATE]
   [END DATE]
   [NOTICE PERIOD]

8. Preserve numerical values exactly as provided.
   Do not change, reinterpret, or guess amounts.

9. Use clear legal-document formatting.

10. Use numbered sections.

11. Include only sections that are relevant to the
    requested agreement.

12. Include a signature section at the end.

13. Do not claim that the agreement is legally valid,
    enforceable, or compliant with any particular law.

14. Do not provide legal advice.

15. Do not add explanations before or after the agreement.

16. End the document after the signature section.

========================
REQUIRED OUTPUT STRUCTURE
========================

TITLE

PARTIES

1. PURPOSE / PROPERTY
2. TERM
3. PAYMENT / FINANCIAL TERMS
4. RESPONSIBILITIES
5. TERMINATION
6. OTHER RELEVANT TERMS
7. SIGNATURES

Adapt the sections to the agreement type.

========================

IMPORTANT:

Your entire response must be the agreement draft.

Start with the agreement title.

Do not write anything before the title.
Do not write anything after the agreement.

Generate the agreement now.
"""

    answer = generate_agreement_response(prompt)

    if not answer:
        raise ValueError(
            "Ollama returned an empty agreement."
        )

    return answer.strip()