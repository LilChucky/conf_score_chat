"""
FastAPI application factory.
Run with:  uvicorn src.api.app:app --reload
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.common.config import AVAILABLE_MODELS
from src.common.logger import get_logger

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan — runs startup / shutdown logic."""
    log.info("AI Chat API starting up — %d models available", len(AVAILABLE_MODELS))
    yield
    log.info("AI Chat API shutting down")


app = FastAPI(
    title="AI Chat API",
    description="Chat API supporting local LLM and Groq models with tool-augmented agents.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def _log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000
    log.info("%s %s → %s (%.1f ms)", request.method, request.url.path, response.status_code, elapsed)
    return response


app.include_router(router)
