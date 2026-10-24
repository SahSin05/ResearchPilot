import pytest

from app.services.retrieval.rrf import reciprocal_rank_fusion


def test_rrf_combines_rankings():
    results = reciprocal_rank_fusion(
        [
            [1, 2, 3],
            [2, 1, 4],
        ]
    )

    assert [result.chunk_id for result in results] == [
        1,
        2,
        3,
        4,
    ]

    assert results[0].score == pytest.approx(
        (1 / 61) + (1 / 62)
    )

    assert results[1].score == pytest.approx(
        (1 / 62) + (1 / 61)
    )


def test_rrf_rejects_invalid_k():
    with pytest.raises(ValueError):
        reciprocal_rank_fusion(
            [[1, 2]],
            k=0,
        )


def test_rrf_handles_empty_lists():
    results = reciprocal_rank_fusion(
        [
            [],
            [5, 6],
        ]
    )

    assert [result.chunk_id for result in results] == [
        5,
        6,
    ]