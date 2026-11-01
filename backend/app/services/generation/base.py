from abc import ABC, abstractmethod
from typing import Sequence


class GenerationProvider(ABC):
    """Abstract interface for LLM generation providers."""

    @abstractmethod
    def generate(
        self,
        question: str,
        context: Sequence[str],
    ) -> str:
        """Generate an answer grounded in the supplied context."""
        raise NotImplementedError