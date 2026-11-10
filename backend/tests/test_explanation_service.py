from app.services.generation.explanation import ExplanationService
from app.services.generation.base import GenerationProvider
from app.services.retrieval.citations import (
    Citation,
    CitedContext,
)


class FakeGenerationProvider(GenerationProvider):
    def generate(
        self,
        question: str,
        context: list[str],
        response_format=None,
    ) -> str:
        return """
        {
          "problem": {
            "content": "The paper studies a research problem.",
            "citations": ["[C1]"]
          },
          "key_concepts": {
            "content": "The paper introduces several important concepts.",
            "citations": ["[C1]", "[C2]"]
          },
          "methodology": {
            "content": "The authors evaluate their proposed approach.",
            "citations": ["[C2]"]
          },
          "dataset": {
            "content": "The supplied evidence describes the dataset.",
            "citations": ["[C3]"]
          },
          "results": {
            "content": "The reported results support the paper's findings.",
            "citations": ["[C4]"]
          },
          "limitations": {
            "content": "The available evidence identifies limitations.",
            "citations": ["[C5]"]
          },
          "glossary": [
            {
              "term": "Research method",
              "definition": "The approach used to investigate the research problem.",
              "citations": ["[C2]"]
            }
          ]
        }
        """


def make_cited_context(
    citation_id: int,
    text: str,
) -> CitedContext:
    citation = Citation(
        citation_id=citation_id,
        chunk_id=citation_id,
        document_id=1,
        label=f"[C{citation_id}]",
        page_number=citation_id,
        section=None,
        subsection=None,
    )

    return CitedContext(
        citation=citation,
        context_text=(
            f"[C{citation_id}]\n"
            f"{text}"
        ),
    )


def test_explanation_service_parses_structured_response():
    provider = FakeGenerationProvider()

    service = ExplanationService(
        provider=provider,
    )

    explanation = service.explain(
        context=[
            make_cited_context(
                1,
                "Paper evidence about the research problem.",
            ),
            make_cited_context(
                2,
                "Paper evidence about the methodology.",
            ),
            make_cited_context(
                3,
                "Paper evidence about the dataset.",
            ),
            make_cited_context(
                4,
                "Paper evidence about the results.",
            ),
            make_cited_context(
                5,
                "Paper evidence about limitations.",
            ),
        ],
    )

    assert explanation.problem.content == (
        "The paper studies a research problem."
    )

    assert explanation.problem.citations == ["[C1]"]

    assert explanation.methodology.content == (
        "The authors evaluate their proposed approach."
    )

    assert len(explanation.glossary) == 1
    assert explanation.glossary[0].term == "Research method"


def test_explanation_service_rejects_empty_context():
    provider = FakeGenerationProvider()

    service = ExplanationService(
        provider=provider,
    )

    try:
        service.explain(context=[])
    except ValueError as exc:
        assert str(exc) == (
            "Paper explanation requires research context."
        )
    else:
        raise AssertionError(
            "Expected ValueError for empty context."
        )