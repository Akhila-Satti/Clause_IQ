from app.models.user import User


def build_personalization_context(user: User) -> str:
    """
    Build optional personalization context for Qwen.

    Personalization information is included only when
    the user has explicitly given consent.
    """

    if not user.personalization_consent:
        return ""

    context_parts = []

    if user.age is not None:
        context_parts.append(
            f"Age: {user.age}"
        )

    if user.occupation:
        context_parts.append(
            f"Occupation: {user.occupation}"
        )

    if user.income:
        context_parts.append(
            f"Income: {user.income}"
        )

    if user.location:
        context_parts.append(
            f"Location: {user.location}"
        )

    if not context_parts:
        return ""

    return f"""
OPTIONAL USER PERSONALIZATION CONTEXT

The user has explicitly consented to personalization.

{chr(10).join(context_parts)}

PERSONALIZATION RULES:
- Use this information only when it is relevant to the user's request.
- Do not mention personal information unnecessarily.
- Do not expose or repeat personal information unless relevant.
- Do not make assumptions based on age, income, occupation, or location.
- Do not use personalization to make legal determinations.
"""