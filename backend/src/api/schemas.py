from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class Source(BaseModel):
    source: str
    section: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]