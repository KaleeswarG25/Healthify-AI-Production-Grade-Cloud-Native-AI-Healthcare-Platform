from typing import Optional

from pydantic import BaseModel


class AnalyzeTextRequest(BaseModel):
    report_text: str
    filename: Optional[str] = None


class AnalyzeTextResponse(BaseModel):
    analysis_id: str
    analysis: str
    summary: str


class ChatRequest(BaseModel):
    message: str
    analysis_id: str


class ChatResponse(BaseModel):
    response: str
    analysis_id: str