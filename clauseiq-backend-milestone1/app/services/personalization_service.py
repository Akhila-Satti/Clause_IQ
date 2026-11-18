
from app.models.user import User


def build_personalization_context(user: User) -> str:
    """
    Build optional personalization context for Qwen.
    Profile information is used only with explicit consent.
    """

    if not user.personalization_consent:
        return ""

    context_parts = []

    if user.age is not None:
        context_parts.append(f"Age: {user.age}")

    if user.occupation:
        context_parts.append(
            f"Occupation: {user.occupation}"
        )

    if user.income is not None:
        context_parts.append(
            f"Income: {user.income}"
        )

    if user.location:
        context_parts.append(
            f"Location: {user.location}"
        )

    if not context_parts:
        return ""

    return (
        "The user has explicitly consented to "
        "personalisation.\n"
        "Use the following information only when relevant:\n"
        + "\n".join(context_parts)
    )
