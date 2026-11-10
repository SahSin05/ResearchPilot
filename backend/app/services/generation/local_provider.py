from typing import Any, Sequence

import ollama

from app.services.generation.base import GenerationProvider


class LocalGenerationProvider(GenerationProvider):
    """Local LLM generation provider using Ollama."""

    def __init__(
        self,
        model: str = "llama3.2:3b",
    ) -> None:
        self.model = model

    def generate(
        self,
        question: str,
        context: Sequence[str],
        response_format: dict[str, Any] | None = None,
    ) -> str:
        context_text = "\n\n".join(context)

        prompt = f"""
You are ResearchPilot, an AI research assistant.

Answer the user's request using ONLY the supplied research evidence.

Rules:
- Do not invent facts.
- Do not use outside knowledge.
- If the evidence is insufficient, clearly say that the available evidence
  is insufficient.
- Preserve citation labels such as [C1], [C2] when they support your answer.

Research evidence:
{context_text}

User request:
{question}
""".strip()

        chat_options: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a research assistant. "
                        "Use only the supplied evidence."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        }

        if response_format is not None:
            chat_options["format"] = response_format

        response = ollama.chat(**chat_options)

        answer = response["message"]["content"]

        if not answer:
            raise RuntimeError(
                "The local generation provider returned an empty response."
            )

        return answer