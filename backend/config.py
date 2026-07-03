"""
Configuration module — loads settings from Streamlit secrets, environment
variables, or the local .env file (in that priority order).
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env from the backend directory (for local development)
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_env_path)

# Resolve CHROMA_PERSIST_DIR relative to the project root so it works
# regardless of the working directory (important for Streamlit Cloud).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_default_chroma = str(_PROJECT_ROOT / "data" / "chroma_db_v2")


def _get_secret(key: str, default: str = "") -> str:
    """
    Try to read a secret from Streamlit Cloud secrets first,
    then fall back to environment variables / .env.
    """
    # 1. Try Streamlit secrets (for Streamlit Cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            val = st.secrets[key]
            logger.info(f"Config: loaded '{key}' from st.secrets")
            return val
    except Exception as e:
        logger.debug(f"Config: st.secrets not available for '{key}': {e}")

    # 2. Fall back to environment variables / dotenv
    val = os.getenv(key, default)
    if val and val != default:
        logger.info(f"Config: loaded '{key}' from environment")
    return val


class Settings:
    """
    Application settings — uses properties so values are resolved
    lazily at access time, not at module import time. This is critical
    for Streamlit Cloud where st.secrets may not be available during
    the initial import phase.
    """

    @property
    def GROQ_API_KEY(self) -> str:
        if not hasattr(self, "_groq_api_key") or not self._groq_api_key:
            self._groq_api_key = _get_secret("GROQ_API_KEY")
        return self._groq_api_key

    @property
    def EMBEDDING_MODEL(self) -> str:
        if not hasattr(self, "_embedding_model"):
            self._embedding_model = _get_secret(
                "EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"
            )
        return self._embedding_model

    @property
    def LLM_MODEL(self) -> str:
        if not hasattr(self, "_llm_model"):
            self._llm_model = _get_secret("LLM_MODEL", "llama-3.3-70b-versatile")
        return self._llm_model

    @property
    def CHROMA_PERSIST_DIR(self) -> str:
        if not hasattr(self, "_chroma_persist_dir"):
            self._chroma_persist_dir = _get_secret(
                "CHROMA_PERSIST_DIR", _default_chroma
            )
        return self._chroma_persist_dir

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

