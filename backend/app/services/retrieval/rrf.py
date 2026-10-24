from dataclasses import dataclass


@dataclass
class RRFResult:
    chunk_id: int
    score: float


def reciprocal_rank_fusion(
    ranked_lists: list[list[int]],
    k: int = 60,
) -> list[RRFResult]:
    if k <= 0:
        raise ValueError("k must be greater than zero.")

    scores: dict[int, float] = {}

    for ranked_list in ranked_lists:
        for rank, chunk_id in enumerate(ranked_list, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + (
                1.0 / (k + rank)
            )

    results = [
        RRFResult(
            chunk_id=chunk_id,
            score=score,
        )
        for chunk_id, score in scores.items()
    ]

    results.sort(
        key=lambda result: result.score,
        reverse=True,
    )

    return results

