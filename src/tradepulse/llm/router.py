import os
from typing import Callable


def choose_provider() -> str:
    if os.getenv("BAILIAN_API_KEY"):
        return "bailian"
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    return "none"


def call_with_fallback(
    prompt: str,
    bailian_call: Callable[[str], str],
    gemini_call: Callable[[str], str],
) -> str:
    provider = choose_provider()

    if provider == "bailian":
        try:
            return bailian_call(prompt)
        except Exception:
            if os.getenv("GEMINI_API_KEY"):
                return gemini_call(prompt)
            raise

    if provider == "gemini":
        return gemini_call(prompt)

    raise RuntimeError("No LLM provider configured")
