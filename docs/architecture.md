# Architecture — Chat

## 1. Executive Summary

Chat is a Python-based AI chat application with a modular, layered architecture: a **Streamlit UI** communicates via HTTP with a **FastAPI REST API**, which delegates to a **LangGraph ReAct agent** in the core layer. The agent can invoke tools (currently DuckDuckGo web search) autonomously. Models are served either locally through a **LiteLLM proxy / Ollama** stack or remotely via the **Groq API**. All local infrastructure runs in Docker containers.

## 2. Architecture Pattern

**Modular Layered Architecture** with four packages under `src/`:

| Package | Purpose | Key Modules |
|---------|---------|-------------|
| `src/common/` | Shared utilities | `config.py` — env settings, model registry, model factory<br>`logger.py` — rotating file + console logging |
| `src/core/` | Business logic | `agent.py` — LangGraph ReAct agent + callback logger<br>`tools.py` — tool definitions (web search)<br>`chat.py` — public chat service interface |
| `src/api/` | REST API layer | `app.py` — FastAPI application factory<br>`routes.py` — endpoint definitions<br>`schemas.py` — Pydantic request/response models |
| `src/ui/` | Frontend | `chat.py` — Streamlit chat UI |
| `docker/` | Infrastructure | Docker Compose (Ollama + LiteLLM) |

### Data Flow

```
User Input → Streamlit UI (src/ui/chat.py)
                  │  HTTP POST /chat
                  ▼
          FastAPI API (src/api/)
                  │  _to_langchain() → core_chat()
                  ▼
         Chat Service (src/core/chat.py)
                  │  run_agent()
                  ▼
       LangGraph Agent (src/core/agent.py)
              ┌───┴───┐
              │       │
         Tool Calls   LLM Calls
    (src/core/tools.py)  │
              │       ├── ChatOpenAI → LiteLLM → Ollama (local)
              │       └── ChatGroq → Groq API   (cloud)
              ▼
       DuckDuckGo Search
              │
              ▼
       Agent composes final AIMessage
                  │
                  ▼
          FastAPI → JSON response → Streamlit UI → User
```

## 3. Component Details

### 3.1 Streamlit UI (`src/ui/chat.py`)

- **Responsibilities:** User interaction, chat history management (session state), model/temperature/system-prompt selection
- **Communication:** HTTP calls to FastAPI backend (`GET /models`, `POST /chat`)
- **Key patterns:**
  - `st.session_state.messages` — In-memory chat history (list of dicts)
  - Sidebar controls for model picker, temperature slider, system prompt
  - Error handling with user-friendly messages for API failures
- **Entry point:** `streamlit run src/ui/chat.py`

### 3.2 FastAPI API (`src/api/`)

- **`app.py`** — Application factory, CORS middleware, request logging middleware, startup hook
- **`routes.py`** — Three endpoints:
  - `GET /health` — liveness check
  - `GET /models` — returns available models and default
  - `POST /chat` — accepts messages, routes to core chat service
- **`schemas.py`** — Pydantic models: `Message`, `ChatRequest`, `ChatResponse`, `ModelsResponse`
- **Entry point:** `uvicorn src.api.app:app --reload`
- **Interactive docs:** `http://localhost:8000/docs`

### 3.3 Core Business Logic (`src/core/`)

- **`chat.py`** — Public interface: `chat(messages, model_name, temperature) → AIMessage`
- **`agent.py`** — LangGraph ReAct agent:
  - `build_agent()` — creates a compiled graph with model + tools
  - `run_agent()` — invokes the graph, returns final `AIMessage`
  - `AgentLogger` — LangChain callback handler logging LLM turns, tool calls, tool results, and errors
- **`tools.py`** — Tool registry:
  - `web_search` — `DuckDuckGoSearchResults` (5 results, list format)
  - `ALL_TOOLS` — single list for easy extension

### 3.4 Common Utilities (`src/common/`)

- **`config.py`** — Centralized configuration:
  - `LLMConfig` / `GroqConfig` — Pydantic models for provider settings
  - `ModelProvider` — provider identifiers (`LOCAL`, `GROQ`)
  - `AVAILABLE_MODELS` — registry mapping display names to `(provider, model_id)` tuples
  - `get_chat_model()` — factory returning `ChatOpenAI` or `ChatGroq` based on provider
- **`logger.py`** — Shared logging:
  - Console + rotating file handler (`logs/app.log`)
  - Env-configurable: `LOG_LEVEL`, `LOG_FILE`, `LOG_MAX_MB`, `LOG_BACKUPS`
  - Suppresses noisy third-party loggers

### 3.5 Docker Infrastructure (`docker/`)

- **`docker-compose.yml`** — Orchestrates:
  - **Ollama** (port 11434) — Local LLM server with GPU support (NVIDIA CDI)
  - **Model Puller** — Helper that pulls models on startup
  - **LiteLLM Proxy** (port 4000) — OpenAI-compatible API facade
- **`config.yaml`** — LiteLLM model routing configuration

## 4. Configuration Management

### Environment Variables (`.env`)

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_ENDPOINT` | `http://localhost:4000/` | LiteLLM proxy URL |
| `OPENAI_API_KEY` | `my-secret-key` | LiteLLM authentication key |
| `GROQ_API_KEY` | *(empty)* | Groq cloud API key |
| `FASTAPI_URL` | `http://localhost:8000` | Backend URL for Streamlit |
| `PHI3_DEPLOYMENT` | `phi3` | Phi-3 model identifier |
| `GEMMA_DEPLOYMENT` | `gemma:2b` | Gemma model identifier |
| `MISTRAL_DEPLOYMENT` | `mistral` | Mistral model identifier |
| `GPT_DEPLOYMENT` | `gpt-4-turbo` | GPT-4 Turbo model identifier |
| `QWEN_DEPLOYMENT` | `qwen3` | Qwen3 model identifier |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FILE` | `logs/app.log` | Log file path |
| `LOG_MAX_MB` | `10` | Max log file size before rotation |
| `LOG_BACKUPS` | `5` | Number of rotated log files |

## 5. State Management

- **Session-only** — Chat history lives in `st.session_state.messages` (Streamlit session state)
- **No persistent storage** — Conversations are lost on page refresh or session end
- **No database** — No data models, migrations, or ORM

## 6. Security Considerations

- LiteLLM proxy uses a static API key (`my-secret-key` by default)
- All local traffic stays on Docker bridge network
- No authentication on the Streamlit UI or FastAPI endpoints
- CORS wide open (`*`) — tighten for production
- `.env` file excluded from Git via `.gitignore`
- Groq API key stored in `.env`, never logged

## 7. Testing

- `tests/` directory exists but is **empty**
- No test framework configured
- Agent callback handler provides runtime observability as a partial substitute

## 8. Deployment

- **Local development:** Docker Compose for LLM infrastructure + `uvicorn` for API + `streamlit run` for UI
- **No CI/CD pipelines** configured
- **No production deployment** configuration
- GPU support available via NVIDIA CDI in Docker Compose
