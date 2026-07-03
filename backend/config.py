"""
Configuration module — loads environment variables from .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the backend directory
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_env_path)


class Settings:
    """Application settings loaded from environment variables."""

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")

    def validate(self) -> None:
        """Ensure critical settings are present."""
        if not self.GROQ_API_KEY or self.GROQ_API_KEY == "your_key_here":
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Please add your Groq API key to backend/.env"
            )


# Singleton instance
settings = Settings()
