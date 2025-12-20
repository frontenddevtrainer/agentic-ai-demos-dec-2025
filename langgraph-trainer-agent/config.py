from __future__ import annotations

from dataclasses import dataclass
import os


def _env(key: str, default: str | None = None, required: bool = False) -> str | None:
    value = os.getenv(key, default)
    if required and not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


def _env_int(key: str, default: int) -> int:
    value = os.getenv(key)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"{key} must be an integer") from exc


@dataclass
class Settings:
    openai_api_key: str
    openai_model: str
    openai_classifier_model: str
    openai_embedding_model: str
    telegram_bot_token: str
    telegram_allowed_chat_id: int | None
    kb_dir: str
    vectorstore_dir: str
    chunk_size: int
    chunk_overlap: int
    top_k: int


def load_settings() -> Settings:
    allowed_chat = _env("TELEGRAM_ALLOWED_CHAT_ID")
    return Settings(
        openai_api_key=_env("OPENAI_API_KEY", required=True),
        openai_model=_env("OPENAI_MODEL", "gpt-4o-mini"),
        openai_classifier_model=_env("OPENAI_CLASSIFIER_MODEL", "gpt-4o-mini"),
        openai_embedding_model=_env("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        telegram_bot_token=_env("TELEGRAM_BOT_TOKEN", required=True),
        telegram_allowed_chat_id=int(allowed_chat) if allowed_chat else None,
        kb_dir=_env("KB_DIR", "kb"),
        vectorstore_dir=_env("VECTORSTORE_DIR", "vectorstore"),
        chunk_size=_env_int("CHUNK_SIZE", 800),
        chunk_overlap=_env_int("CHUNK_OVERLAP", 100),
        top_k=_env_int("TOP_K", 4),
    )