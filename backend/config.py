"""
Configuration module — loads settings from Streamlit secrets, environment
variables, or the local .env file (in that priority order).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the backend directory (for local development)
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_env_path)


def _get_secret(key: str, default: str = "") -> str:
    """
    Try to read a secret from Streamlit Cloud secrets first,
    then fall back to environment variables / .env.
    """
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


# Resolve CHROMA_PERSIST_DIR relative to the project root so it works
# regardless of the working directory (important for Streamlit Cloud).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_default_chroma = str(_PROJECT_ROOT / "data" / "chroma_db")


class Settings:
    """Application settings loaded from environment variables."""

    GROQ_API_KEY: str = _get_secret("GROQ_API_KEY")
    EMBEDDING_MODEL: str = _get_secret("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5")
    LLM_MODEL: str = _get_secret("LLM_MODEL", "llama-3.3-70b-versatile")
    CHROMA_PERSIST_DIR: str = _get_secret("CHROMA_PERSIST_DIR", _default_chroma)

    def validate(self) -> None:
        """Ensure critical settings are present."""
        if not self.GROQ_API_KEY or self.GROQ_API_KEY == "your_key_here":
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Please add your Groq API key to backend/.env "
                "or to Streamlit Cloud Secrets."
            )


# Singleton instance
settings = Settings()
