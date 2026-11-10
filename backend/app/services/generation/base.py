from abc import ABC, abstractmethod
from typing import Sequence, Any


class GenerationProvider(ABC):
    """Abstract interface for LLM generation providers."""

    @abstractmethod
    def generate(
        self,
        question: str,
        context: Sequence[str],
        response_format: dict[str, Any] | None=None
    ) -> str:
        """Generate an answer grounded in the supplied context."""
        raise NotImplementedError