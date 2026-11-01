import os
from typing import Sequence

from openai import OpenAI

from app.services.generation.base import GenerationProvider


class OpenAIProvider(GenerationProvider):
    """OpenAI-backed implementation of the generation provider."""

    def __init__(
        self,
        model: str | None = None,
    ) -> None:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = OpenAI(api_key=api_key)
        self.model = model or os.getenv(
            "OPENAI_GENERATION_MODEL",
            "gpt-4o-mini",
        )

    def generate(
        self,
        question: str,
        context: Sequence[str],
    ) -> str:
        context_text = "\n\n".join(context)

        prompt = f"""
You are ResearchPilot, an AI research assistant.

Answer the user's question using only the supplied research evidence.

If the evidence does not contain enough information to answer the question,
say that the available evidence is insufficient. Do not invent facts.

Research evidence:
{context_text}

User question:
{question}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You answer research questions using only "
                        "the provided evidence."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.0,
        )

        answer = response.choices[0].message.content

        if not answer:
            raise RuntimeError(
                "The generation provider returned an empty response."
            )

        return answer