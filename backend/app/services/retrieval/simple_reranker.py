import re

from app.services.retrieval.reranker import (
    RerankResult,
    Reranker,
)


class SimpleReranker(Reranker):

    def rerank(
        self,
        query: str,
        documents: list[tuple[int, str]],
    ) -> list[RerankResult]:

        query_terms = set(
            re.findall(
                r"\b\w+\b",
                query.lower(),
            )
        )

        results = []

        for chunk_id, text in documents:
            document_terms = set(
                re.findall(
                    r"\b\w+\b",
                    text.lower(),
                )
            )

            if not document_terms:
                score = 0.0
            else:
                overlap = query_terms & document_terms

                score = len(overlap) / len(query_terms)

            results.append(
                RerankResult(
                    chunk_id=chunk_id,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results