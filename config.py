"""
CineMind — Centralised application configuration.

All settings are loaded from environment variables (with ``.env`` support).
Import the singleton via :func:`get_settings` to avoid re-reading the
environment on every access.

Usage::

    from config import get_settings
    settings = get_settings()
    print(settings.GROQ_API_KEY)
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class Settings(BaseSettings):
    """Typed, validated application settings.

    Values are read from environment variables first, then from the ``.env``
    file in the project root.  Pydantic validates types and applies defaults
    automatically.
    """

    # --- Groq LLM ---------------------------------------------------------
    GROQ_API_KEY: str = Field(
        default="",
        description="Groq API key (free at https://console.groq.com/keys)",
    )
    GROQ_BASE_URL: str = Field(
        default="https://api.groq.com/openai/v1",
        description="Groq-compatible OpenAI base URL",
    )
    GROQ_MODEL: str = Field(
        default="llama-3.1-8b-instant",
        description="LLM model identifier for Groq inference",
    )

    # --- Server ------------------------------------------------------------
    HOST: str = Field(default="127.0.0.1", description="Uvicorn bind host")
    PORT: int = Field(default=8000, ge=1, le=65535, description="Uvicorn bind port")

    # --- CORS --------------------------------------------------------------
    ALLOWED_ORIGINS: str = Field(
        default=(
            "http://localhost:8080,http://127.0.0.1:8080,"
            "http://localhost:8081,http://127.0.0.1:8081,"
            "http://localhost:4173"
        ),
        description="Comma-separated list of allowed CORS origins",
    )

    # --- Data paths --------------------------------------------------------
    CSV_PATH: str = Field(
        default=os.path.join(_ROOT_DIR, "data", "tier1_clean_movies.csv"),
        description="Path to the curated movie CSV dataset",
    )
    EMBEDDINGS_PATH: str = Field(
        default=os.path.join(_ROOT_DIR, "models", "tier1_movie_embeddings.pkl"),
        description="Path to the precomputed sentence-transformer embeddings",
    )
    FRONTEND_DIST: str = Field(
        default=os.path.join(_ROOT_DIR, "frontend", "dist"),
        description="Path to the built React frontend (for production serving)",
    )

    # --- Helpers -----------------------------------------------------------

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse the comma-separated ``ALLOWED_ORIGINS`` string into a list."""
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = os.path.join(_ROOT_DIR, ".env")
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the application settings singleton (cached after first call)."""
    return Settings()
