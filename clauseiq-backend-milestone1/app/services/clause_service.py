import re
from dataclasses import dataclass


@dataclass
class ClauseData:
    section: str
    title: str
    text: str
    category: str
    risk_level: str
    explanation: str


CATEGORY_KEYWORDS = {
    "Privacy": ["personal data", "personal information", "privacy", "tracking", "location"],
    "Financial": ["payment", "fee", "charge", "subscription", "renew", "price", "billing"],
    "Cancellation": ["cancel", "termination", "terminate", "notice period", "early termination"],
    "Data": ["retain", "retention", "delete data", "data storage", "data processing"],
    "Intellectual Property": ["copyright", "intellectual property", "license", "ownership", "content"],
    "Contractual": ["arbitration", "indemnif", "liability", "governing law", "jurisdiction"],
    "Account": ["account suspension", "suspend", "account termination", "loss of access"],
    "Changes": ["modify these terms", "change these terms", "changes to the terms", "update the terms"],
}


def clean_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def classify_clause(text: str) -> tuple[str, str]:
    lower = text.lower()
    matches = [
        category
        for category, keywords in CATEGORY_KEYWORDS.items()
        if any(keyword in lower for keyword in keywords)
    ]

    category = matches[0] if matches else "General"

    high_signals = [
        "automatically renew",
        "automatic renewal",
        "indemnif",
        "arbitration",
        "share your personal",
        "third parties",
        "non-refundable",
        "unlimited license",
    ]
    medium_signals = [
        "may change",
        "retain",
        "termination",
        "license",
        "payment",
        "personal information",
    ]

    if any(signal in lower for signal in high_signals):
        risk = "HIGH"
    elif any(signal in lower for signal in medium_signals):
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return category, risk


def explain_clause(text: str, category: str) -> str:
    if category == "Privacy":
        return "This provision relates to how personal or usage information may be collected, used, shared, or tracked."
    if category == "Financial":
        return "This provision may affect payments, charges, subscription costs, billing, or price-related obligations."
    if category == "Cancellation":
        return "This provision may affect when and how the agreement or subscription can be cancelled or terminated."
    if category == "Data":
        return "This provision relates to storage, retention, processing, or deletion of information."
    if category == "Intellectual Property":
        return "This provision relates to ownership, licensing, or permitted use of intellectual property or uploaded content."
    if category == "Contractual":
        return "This provision concerns contractual rights or obligations such as arbitration, liability, indemnification, or governing law."
    return "This clause was extracted from the agreement for review. Its practical meaning should be considered together with the surrounding provisions."


def segment_clauses(document_text: str) -> list[ClauseData]:
    text = clean_text(document_text)

    # First try common numbered/labelled sections.
    pattern = re.compile(
        r"(?im)^(?P<section>"
        r"(?:clause\s+\w+|section\s+[\w.-]+|\d+(?:\.\d+)*)"
        r")\s*(?:[-–—:.)]\s*)?(?P<title>[^\n]*)"
    )
    matches = list(pattern.finditer(text))

    clauses = []

    if matches:
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            if not body:
                continue

            section = match.group("section").strip()
            title = match.group("title").strip() or "Untitled Clause"
            category, risk = classify_clause(body)
            clauses.append(
                ClauseData(
                    section=section,
                    title=title,
                    text=body,
                    category=category,
                    risk_level=risk,
                    explanation=explain_clause(body, category),
                )
            )

    # Fallback: split on blank paragraphs if no numbered sections were detected.
    if not clauses:
        blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
        for index, block in enumerate(blocks, start=1):
            first_line, *rest = block.split("\n", 1)
            title = first_line[:120]
            body = rest[0].strip() if rest else block
            category, risk = classify_clause(body)
            clauses.append(
                ClauseData(
                    section=f"Section {index}",
                    title=title,
                    text=body,
                    category=category,
                    risk_level=risk,
                    explanation=explain_clause(body, category),
                )
            )

    return clauses
