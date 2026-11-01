from typing import Sequence

from app.services.generation.base import GenerationProvider


class GenerationService:
    """Application service for grounded answer generation."""

    def __init__(self, provider: GenerationProvider) -> None:
        self.provider = provider

    def generate_answer(
        self,
        question: str,
        context: Sequence[str],
    ) -> str:
        if not question.strip():
            raise ValueError("Question cannot be empty.")

        if not context:
            raise ValueError("Generation requires research context.")

        return self.provider.generate(
            question=question,
            context=context,
        )