"""
Standalone test script for the Ollama service.

Run from the backend directory:
    python -m tests.test_ollama

Requires Ollama to be running with llama3.2:1b and nomic-embed-text pulled.
"""

import asyncio
import sys

# Allow running from the backend directory
sys.path.insert(0, ".")

from app.services.ollama_service import (
    generate,
    get_embedding,
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaServiceError,
)


async def test_generate():
    print("=" * 60)
    print("TEST 1: Text Generation (llama3.2:1b)")
    print("=" * 60)
    prompt = "What is RAG in AI? Answer in one sentence."
    print(f"Prompt : {prompt}")
    try:
        result = await generate(prompt)
        print(f"Response: {result.strip()}")
        print("[PASS] Generation test PASSED")
        return True
    except OllamaConnectionError as e:
        print(f"[FAIL] Connection error: {e}")
    except OllamaModelNotFoundError as e:
        print(f"[FAIL] Model not found: {e}")
    except OllamaServiceError as e:
        print(f"[FAIL] Service error: {e}")
    return False


async def test_embedding():
    print()
    print("=" * 60)
    print("TEST 2: Text Embedding (nomic-embed-text)")
    print("=" * 60)
    text = "DocuMind AI uses retrieval-augmented generation."
    print(f"Input  : {text}")
    try:
        vector = await get_embedding(text)
        print(f"Vector length : {len(vector)}")
        print(f"First 5 values: {vector[:5]}")
        print("[PASS] Embedding test PASSED")
        return True
    except OllamaConnectionError as e:
        print(f"[FAIL] Connection error: {e}")
    except OllamaModelNotFoundError as e:
        print(f"[FAIL] Model not found: {e}")
    except OllamaServiceError as e:
        print(f"[FAIL] Service error: {e}")
    return False


async def main():
    gen_ok = await test_generate()
    emb_ok = await test_embedding()
    print()
    if gen_ok and emb_ok:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED - check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
