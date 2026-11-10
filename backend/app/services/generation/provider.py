import os

from app.services.generation.base import GenerationProvider
from app.services.generation.groq_provider import (
    GroqGenerationProvider,
)
from app.services.generation.local_provider import (
    LocalGenerationProvider,
)


def create_generation_provider() -> GenerationProvider:
    """
    Create the configured LLM generation provider.

    Supported providers:
    - groq
    - local
    """

    provider_name = os.getenv(
        "GENERATION_PROVIDER",
        "local",
    ).strip().lower()

    if provider_name == "groq":
        return GroqGenerationProvider()

    if provider_name == "local":
        return LocalGenerationProvider()

    raise RuntimeError(
        f"Unsupported generation provider: {provider_name}"
    )