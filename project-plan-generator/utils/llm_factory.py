"""Factory for creating LLM instances based on configuration."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def get_llm(temperature: float = 0.7, model: Optional[str] = None):
    """
    Get an LLM instance based on environment configuration.

    Args:
        temperature: Temperature for response generation
        model: Optional model override

    Returns:
        LLM instance (OpenAI or Anthropic)
    """
    provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
    default_model = os.getenv("LLM_MODEL")

    if model is None:
        model = default_model

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model or "gpt-4-turbo-preview",
            temperature=temperature,
        )
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model or "claude-3-5-sonnet-20241022",
            temperature=temperature,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
