from pydantic import BaseModel, Field


class ExplanationSection(BaseModel):
    content: str = Field(
        min_length=1,
    )
    citations: list[str] = Field(
        default_factory=list,
    )


class GlossaryEntry(BaseModel):
    term: str = Field(
        min_length=1,
    )
    definition: str = Field(
        min_length=1,
    )
    citations: list[str] = Field(
        default_factory=list,
    )


class PaperExplanation(BaseModel):
    problem: ExplanationSection
    key_concepts: ExplanationSection
    methodology: ExplanationSection
    dataset: ExplanationSection
    results: ExplanationSection
    limitations: ExplanationSection
    glossary: list[GlossaryEntry] = Field(
        default_factory=list,
    )