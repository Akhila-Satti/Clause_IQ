import requests

from app.core.config import settings


OLLAMA_URL = f"{settings.OLLAMA_URL}/api/chat"
OLLAMA_MODEL = settings.OLLAMA_MODEL
OLLAMA_TIMEOUT = settings.OLLAMA_TIMEOUT


def generate_response(
    prompt: str,
    temperature: float = 0.2,
) -> str:
    """
    Generate a text response using the locally running Ollama model.
    """

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "stream": False,
        "think": False,
        "options": {
            "temperature": temperature,
        },
    }
    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=OLLAMA_TIMEOUT,
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not connect to Ollama at {settings.OLLAMA_URL}: {exc}"
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "Ollama returned an invalid JSON response."
        ) from exc

    message = data.get("message", {})
    answer = message.get("content", "")

    if not answer:
        raise ValueError(
            "Ollama returned an empty response."
        )

    return answer.strip()


def generate_json_response(
    prompt: str,
    temperature: float = 0.1,
) -> str:
    """
    Generate a JSON response using Ollama.

    Ollama is instructed to return JSON so that
    ClauseIQ can safely parse structured analysis.
    """

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "stream": False,
        "think": False,
        "format": "json",
        "options": {
            "temperature": temperature,
        },
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=OLLAMA_TIMEOUT,
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not connect to Ollama at {settings.OLLAMA_URL}: {exc}"
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "Ollama returned an invalid JSON response."
        ) from exc

    message = data.get("message", {})
    answer = message.get("content", "")

    if not answer:
        raise ValueError(
            "Ollama returned an empty JSON response."
        )

    return answer.strip()