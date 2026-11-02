from types import SimpleNamespace

import pytest

from app.services.explanation import ExplanationService


class FakeProvider:
    def __init__(self, response="## Paper overview\nA grounded overview [C1]."):
        self.response = response
        self.question = None
        self.context = None

    def generate(self, question, context):
        self.question = question
        self.context = context
        return self.response


def make_context():
    return SimpleNamespace(
        chunk_id=12,
        document_id=4,
        page_number=3,
        section="Methods",
        subsection="Training",
        context_text="The authors trained the model on the reported dataset.",
    )


def test_explanation_service_builds_cited_context():
    provider = FakeProvider()
    service = ExplanationService(provider)

    explanation, citations = service.generate(
        filename="paper.pdf",
        context_items=[make_context()],
    )

    assert "Paper overview" in explanation
    assert len(citations) == 1
    assert citations[0].label == "[C1]"
    assert citations[0].page_number == 3
    assert "[C1]" in provider.context[0]
    assert "Page: 3" in provider.context[0]
    assert "Methods" in provider.context[0]


def test_explanation_service_rejects_empty_evidence():
    service = ExplanationService(FakeProvider())

    with pytest.raises(ValueError, match="research evidence"):
        service.generate(
            filename="paper.pdf",
            context_items=[],
        )


def test_explanation_service_rejects_empty_model_response():
    service = ExplanationService(FakeProvider(response="  "))

    with pytest.raises(RuntimeError, match="empty explanation"):
        service.generate(
            filename="paper.pdf",
            context_items=[make_context()],
        )
