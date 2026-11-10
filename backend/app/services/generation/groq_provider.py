import os
from typing import Any, Sequence

from openai import OpenAI

from app.services.generation.base import GenerationProvider


class GroqGenerationProvider(GenerationProvider):
    """
    Cloud LLM generation provider using Groq's
    OpenAI-compatible API.
    """

    def __init__(
        self,
        model: str | None = None,
    ) -> None:
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )

        self.model = model or os.getenv(
            "GROQ_GENERATION_MODEL",
            "openai/gpt-oss-20b",
        )

    def generate(
        self,
        question: str,
        context: Sequence[str],
        response_format: dict[str, Any] | None = None,
    ) -> str:
        if not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        if not context:
            raise ValueError(
                "Generation requires research context."
            )

        context_text = "\n\n".join(context)

        prompt = f"""
You are ResearchPilot, an AI research assistant.

Answer the user's request using ONLY the supplied research evidence.

Rules:
- Do not invent facts.
- Do not use outside knowledge.
- If the evidence is insufficient, clearly say so.
- Preserve citation labels such as [C1], [C2], [C3].
- Only use a citation label when the supplied evidence supports the claim.
- Do not create citation labels that do not exist in the supplied evidence.

Research evidence:
{context_text}

User request:
{question}
""".strip()

        request: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are ResearchPilot, a research assistant "
                        "that answers only from supplied evidence."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.1,
            "max_completion_tokens": 3000,
        }

        if response_format is not None:
            request["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "paper_explanation",
                    "strict": True,
                    "schema": response_format,
                },
            }

        response = self.client.chat.completions.create(
            **request
        )

        answer = response.choices[0].message.content

        if not answer:
            raise RuntimeError(
                "The Groq generation provider returned "
                "an empty response."
            )

        return answer