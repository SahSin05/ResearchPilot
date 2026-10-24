from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RerankResult:
    chunk_id: int
    score: float


class Reranker(ABC):

    @abstractmethod
    def rerank(
        self,
        query: str,
        documents: list[tuple[int, str]],
    ) -> list[RerankResult]:
        raise NotImplementedError