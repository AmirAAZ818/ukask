"""Request and response shapes for the API. Kept separate from main.py so
they're easy to read on their own and reuse later, e.g. for generating
TypeScript types for the frontend."""

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Question in Persian about a university regulation.",
    )
    k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of chunks to retrieve before generating an answer.",
    )


class SourceItem(BaseModel):
    text: str
    source_file: str | None = None
    page: int | None = None
    title: str | None = None
    article_numbers: str | None = None
    chunk_type: str | None = None
    similarity: float


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceItem]


class HealthResponse(BaseModel):
    status: str
    index_ready: bool
    embedding_model_ready: bool