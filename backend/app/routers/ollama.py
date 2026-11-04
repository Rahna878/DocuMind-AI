"""
Temporary test endpoints for the Ollama service.

These verify that generation and embedding work end-to-end.
Remove or replace once the full RAG pipeline is implemented.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ollama_service import (
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaServiceError,
    generate,
    get_embedding,
)

router = APIRouter(prefix="/ollama", tags=["ollama"])


# --------------- Request / Response schemas ---------------

class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    prompt: str
    response: str


class EmbedRequest(BaseModel):
    text: str


class EmbedResponse(BaseModel):
    text: str
    vector_length: int
    embedding_preview: list[float]  # first 5 values only


# --------------- Endpoints ---------------

@router.post("/generate", response_model=GenerateResponse)
async def test_generate(body: GenerateRequest):
    """Send a prompt to the chat model and return the response."""
    try:
        result = await generate(body.prompt)
    except OllamaConnectionError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except OllamaModelNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except OllamaServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return GenerateResponse(prompt=body.prompt, response=result)


@router.post("/embed", response_model=EmbedResponse)
async def test_embed(body: EmbedRequest):
    """Generate an embedding and return its length plus a short preview."""
    try:
        vector = await get_embedding(body.text)
    except OllamaConnectionError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except OllamaModelNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except OllamaServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return EmbedResponse(
        text=body.text,
        vector_length=len(vector),
        embedding_preview=vector[:5],
    )

