"""
Pydantic request/response schemas for the chat API.
"""

from pydantic import BaseModel, Field

from src.common.config import DEFAULT_MODEL


class Message(BaseModel):
    role: str = Field(..., description="'user', 'assistant', or 'system'")
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    model: str = DEFAULT_MODEL
    temperature: float | None = None


class ChatResponse(BaseModel):
    content: str
    model: str


class ModelsResponse(BaseModel):
    models: list[str]
    default: str
