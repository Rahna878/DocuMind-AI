"""
Reusable Ollama service for DocuMind AI.

Provides two core capabilities via Ollama's local HTTP API:
  - Text generation  (llama3.2:1b)
  - Text embedding   (nomic-embed-text)
"""

import httpx

OLLAMA_BASE_URL = "http://localhost:11434"
CHAT_MODEL = "llama3.2:1b"
EMBEDDING_MODEL = "nomic-embed-text"

# Generous timeout: small models are fast, but first load can be slow
_TIMEOUT = httpx.Timeout(120.0, connect=10.0)


class OllamaServiceError(Exception):
    """Base exception for Ollama service errors."""


class OllamaConnectionError(OllamaServiceError):
    """Raised when the Ollama server is unreachable."""


class OllamaModelNotFoundError(OllamaServiceError):
    """Raised when the requested model is not available."""


async def generate(prompt: str, *, model: str = CHAT_MODEL) -> str:
    """Send a prompt to Ollama and return the generated text.

    Args:
        prompt: The text prompt to send.
        model:  The model name (defaults to CHAT_MODEL).

    Returns:
        The generated response string.

    Raises:
        OllamaConnectionError: If the Ollama server is unreachable.
        OllamaModelNotFoundError: If the model is not pulled / available.
        OllamaServiceError: For any other Ollama API error.
    """
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.post(url, json=payload)
    except httpx.ConnectError as exc:
        raise OllamaConnectionError(
            f"Cannot connect to Ollama at {OLLAMA_BASE_URL}. "
            "Is the Ollama server running?"
        ) from exc
    except httpx.TimeoutException as exc:
        raise OllamaServiceError(
            "Request to Ollama timed out. The model may still be loading."
        ) from exc

    if response.status_code == 404:
        raise OllamaModelNotFoundError(
            f"Model '{model}' not found. Run:  ollama pull {model}"
        )
    if response.status_code != 200:
        raise OllamaServiceError(
            f"Ollama returned status {response.status_code}: {response.text}"
        )

    data = response.json()
    return data.get("response", "")


async def get_embedding(text: str, *, model: str = EMBEDDING_MODEL) -> list[float]:
    """Generate an embedding vector for the given text.

    Args:
        text:  The input text to embed.
        model: The embedding model name (defaults to EMBEDDING_MODEL).

    Returns:
        A list of floats representing the embedding vector.

    Raises:
        OllamaConnectionError: If the Ollama server is unreachable.
        OllamaModelNotFoundError: If the model is not pulled / available.
        OllamaServiceError: For any other Ollama API error.
    """
    url = f"{OLLAMA_BASE_URL}/api/embed"
    payload = {"model": model, "input": text}

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.post(url, json=payload)
    except httpx.ConnectError as exc:
        raise OllamaConnectionError(
            f"Cannot connect to Ollama at {OLLAMA_BASE_URL}. "
            "Is the Ollama server running?"
        ) from exc
    except httpx.TimeoutException as exc:
        raise OllamaServiceError(
            "Request to Ollama timed out. The model may still be loading."
        ) from exc

    if response.status_code == 404:
        raise OllamaModelNotFoundError(
            f"Model '{model}' not found. Run:  ollama pull {model}"
        )
    if response.status_code != 200:
        raise OllamaServiceError(
            f"Ollama returned status {response.status_code}: {response.text}"
        )

    data = response.json()

    # /api/embed returns {"embeddings": [[...], ...]}
    embeddings = data.get("embeddings")
    if not embeddings or not embeddings[0]:
        raise OllamaServiceError("Ollama returned an empty embedding.")

    return embeddings[0]

