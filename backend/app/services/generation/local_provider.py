from typing import Sequence

import ollama

from app.services.generation.base import GenerationProvider


class LocalGenerationProvider(GenerationProvider):
    """Local LLM generation provider using Ollama."""

    def __init__(self, model: str = "llama3.2:3b") -> None:
        self.model = model

    def generate(self, question: str, context: Sequence[str]) -> str:
        context_text = "\n\n".join(context)

        prompt = f"""
You are ResearchPilot, an AI research assistant.

Answer the user's question using ONLY the supplied research evidence.

Rules:
- Do not invent facts.
- Do not use outside knowledge.
- If the evidence is insufficient, clearly say that the available evidence
  is insufficient to answer the question.
- Give a concise, research-oriented answer.
- Preserve citation labels such as [C1], [C2] when they support your answer.

Research evidence:
{context_text}

User question:
{question}
"""

        response = ollama.chat(
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
        )

        answer = response["message"]["content"]

        if not answer:
            raise RuntimeError(
                "The local generation provider returned an empty response."
            )

        return answer

    