from app.services.generation.base import GenerationProvider
from app.services.retrieval.citations import build_citations
from app.services.retrieval.context import ContextItem


EXPLANATION_PROMPT = """Create a structured, detailed explanation of the research paper
using ONLY the supplied evidence. Write in clear technical language suitable for a
reader learning the paper.

Use these Markdown sections:
1. Paper overview and summary
2. Research problem and objectives
3. Key concepts and prerequisites
4. Methodology (explain the steps in order)
5. Dataset and experimental setup
6. Results and interpretation
7. Limitations, assumptions, and threats to validity
8. Technical glossary

Ground every factual claim in the supplied evidence and preserve citation labels
such as [C1]. Do not invent missing details, numerical results, datasets, authors,
or conclusions. If a requested section is not supported by the evidence, explicitly
write "Not specified in the retrieved paper evidence." Distinguish the paper's
reported findings from your explanation or interpretation. Do not claim that the
retrieved excerpts represent the entire paper.
"""


class ExplanationService:
    """Generate a structured, evidence-grounded explanation for a paper."""

    def __init__(self, provider: GenerationProvider) -> None:
        self.provider = provider

    def generate(
        self,
        filename: str,
        context_items: list[ContextItem],
    ) -> tuple[str, list]:
        if not context_items:
            raise ValueError("Explanation requires research evidence.")

        citations = build_citations(context_items)
        cited_context = [
            f"{citation.label}\n"
            f"Document: {filename}\n"
            f"Page: {citation.page_number if citation.page_number is not None else 'not available'}\n"
            f"Section: {citation.section or 'not available'}\n"
            f"{item.context_text}"
            for citation, item in zip(citations, context_items)
        ]

        explanation = self.provider.generate(
            question=EXPLANATION_PROMPT,
            context=cited_context,
        )
        if not explanation or not explanation.strip():
            raise RuntimeError("The generation provider returned an empty explanation.")

        return explanation.strip(), citations
