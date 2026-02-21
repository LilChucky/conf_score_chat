"""
API route definitions.
"""

from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from src.api.schemas import Message, ChatRequest, ChatResponse, ModelsResponse
from src.common.config import AVAILABLE_MODELS, DEFAULT_MODEL
from src.common.logger import get_logger
from src.core.chat import chat as core_chat

log = get_logger(__name__)

router = APIRouter()

# ── Helpers ──────────────────────────────────────────────────
_ROLE_MAP = {
    "user": HumanMessage,
    "assistant": AIMessage,
    "system": SystemMessage,
}


def _to_langchain(messages: list[Message]):
    """Convert API message schemas to LangChain message objects."""
    result = []
    for msg in messages:
        cls = _ROLE_MAP.get(msg.role)
        if cls is None:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown role '{msg.role}'. Must be 'user', 'assistant', or 'system'.",
            )
        result.append(cls(content=msg.content))
    return result


# ── Routes ───────────────────────────────────────────────────
@router.get("/health")
async def health():
    log.debug("Health check")
    return {"status": "ok"}


@router.get("/models", response_model=ModelsResponse)
async def get_models():
    """Return available model names and the default."""
    log.debug("Models requested")
    return ModelsResponse(models=list(AVAILABLE_MODELS.keys()), default=DEFAULT_MODEL)


@router.post("/chat", response_model=ChatResponse)
async def post_chat(req: ChatRequest):
    """Send a conversation to the selected model and return its reply."""
    if req.model not in AVAILABLE_MODELS:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown model '{req.model}'. Call GET /models for available options.",
        )

    log.info("Chat request: model=%s, messages=%d, temperature=%s", req.model, len(req.messages), req.temperature)
    try:
        lc_messages = _to_langchain(req.messages)
        response = await core_chat(lc_messages, model_name=req.model, temperature=req.temperature)
        log.info("Chat response: model=%s, reply_length=%d chars", req.model, len(response.content))
        return ChatResponse(content=response.content, model=req.model)
    except HTTPException:
        raise
    except Exception as exc:
        log.exception("Chat error for model=%s: %s", req.model, exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
