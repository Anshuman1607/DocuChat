from pydantic import BaseModel
from typing import Optional

class DocumentResponse(BaseModel):
    message: str
    filename: str
    chunks: int

class QuestionRequest(BaseModel):
    question: str

class SourceDocument(BaseModel):
    content: str
    page: Optional[int]
    source: Optional[str]

class AnswerResponse(BaseModel):
    answer: str
    sources: list[SourceDocument]