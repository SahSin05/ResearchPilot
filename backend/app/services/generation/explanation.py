import json
from typing import Sequence

from pydantic import ValidationError

from app.schemas.explanation import PaperExplanation
from app.services.generation.base import GenerationProvider
from app.services.retrieval.citations import CitedContext


class ExplanationService:
    """Generate a structured, evidence-grounded explanation of a paper."""

    def __init__(self, provider: GenerationProvider) -> None:
        self.provider = provider

    def explain(
        self,
        context: Sequence[CitedContext],
    ) -> PaperExplanation:
        if not context:
            raise ValueError(
                "Paper explanation requires research context."
            )

        context_text = [
            item.context_text
            for item in context
        ]

        prompt = self._build_prompt(context_text)

        raw_response = self.provider.generate(
            question=prompt,
            context=context_text,
            response_format=self._response_schema(),
        )

        return self._parse_response(raw_response)

    @staticmethod
    def _response_schema() -> dict:
        """
        JSON schema used for structured LLM output.

        Groq strict JSON-schema mode requires every object
        to explicitly reject undeclared properties.
        """

        explanation_section = {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "content",
                "citations",
            ],
            "properties": {
                "content": {
                    "type": "string",
                },
                "citations": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
            },
        }

        glossary_entry = {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "term",
                "definition",
                "citations",
            ],
            "properties": {
                "term": {
                    "type": "string",
                },
                "definition": {
                    "type": "string",
                },
                "citations": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
            },
        }

        return {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "problem",
                "key_concepts",
                "methodology",
                "dataset",
                "results",
                "limitations",
                "glossary",
            ],
            "properties": {
                "problem": explanation_section,
                "key_concepts": explanation_section,
                "methodology": explanation_section,
                "dataset": explanation_section,
                "results": explanation_section,
                "limitations": explanation_section,
                "glossary": {
                    "type": "array",
                    "items": glossary_entry,
                },
            },
        }

    @staticmethod
    def _build_prompt(
        context: Sequence[str],
    ) -> str:
        evidence = "\n\n".join(context)

        return f"""
Create a structured explanation of the research paper represented
by the supplied evidence.

Return ONLY valid JSON matching the required response schema.

The response must contain:
- problem
- key_concepts
- methodology
- dataset
- results
- limitations
- glossary

Each explanation section must contain:
- content
- citations

Each glossary entry must contain:
- term
- definition
- citations

Rules:
- Use ONLY the supplied research evidence.
- Do not use outside knowledge.
- Do not invent facts, numbers, datasets, methods, or conclusions.
- If a section is not supported by the evidence, explicitly say so
  in its content.
- Every citation must use an existing citation label such as [C1].
- Do not create citation labels that are not present in the evidence.
- Keep each explanation section concise and focused.
- Prefer approximately 2-4 sentences per explanation section.
- Do not repeat the same information across sections.
- The glossary should contain only the most important technical
  terms supported by the supplied evidence.
- Keep the glossary concise and avoid unnecessary entries.
- Return JSON only.
- Do not wrap the JSON in Markdown code fences.

Research evidence:

{evidence}
""".strip()

    @staticmethod
    def _parse_response(
        raw_response: str,
    ) -> PaperExplanation:
        if not raw_response.strip():
            raise RuntimeError(
                "The explanation provider returned an empty response."
            )

        try:
            data = json.loads(raw_response)

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "The explanation provider returned invalid JSON."
            ) from exc

        try:
            return PaperExplanation.model_validate(data)

        except ValidationError as exc:
            raise RuntimeError(
                "The explanation provider returned JSON that "
                "does not match the expected explanation schema."
            ) from exc