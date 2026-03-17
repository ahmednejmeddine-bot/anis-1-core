"""
Shared LLM service for ANIS-1.
All agents use this module to make OpenAI calls — one place to update
the model, parameters, or error handling.
"""

import os
from openai import OpenAI, OpenAIError

MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.4
DEFAULT_MAX_TOKENS = 1024


class LLMError(Exception):
    """Raised when the LLM call fails or the API key is missing."""


def get_client() -> OpenAI:
    """Return an authenticated OpenAI client, or raise LLMError if the key is missing."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMError(
            "OPENAI_API_KEY is not configured. "
            "Add it to Replit Secrets to enable AI responses."
        )
    return OpenAI(api_key=api_key)


def chat(
    system_prompt: str,
    user_message: str,
    model: str = MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str:
    """
    Send a chat completion request to OpenAI and return the response text.

    Args:
        system_prompt: The agent's role and behavioural instructions.
        user_message:  The user's task or query.
        model:         OpenAI model name (default: gpt-4o).
        temperature:   Sampling temperature (lower = more focused).
        max_tokens:    Maximum tokens in the response.

    Returns:
        The model's response as a plain string.

    Raises:
        LLMError: On missing API key or OpenAI API failure.
    """
    client = get_client()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as exc:
        raise LLMError(f"OpenAI API error: {exc}") from exc
