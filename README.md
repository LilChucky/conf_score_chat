# 💬 AI Chat

A modular AI chat application powered by open-source and cloud LLMs, with a Streamlit interface, FastAPI backend, and a LangGraph agent that can search the web autonomously.

## Features

- **Multi-model support** — Switch between local models (Phi-3, Gemma 2B, Mistral, GPT-4 Turbo, Qwen3 4B) and cloud models (Groq Llama 3.1, Mixtral, GPT-OSS 120B)
- **Tool-augmented agent** — LangGraph ReAct agent with DuckDuckGo web search — the model decides when to search
- **FastAPI backend** — REST API with interactive docs at `/docs`
- **Adjustable temperature** — Control response creativity with a slider (0.0–1.0)
- **Custom system prompts** — Set the assistant's personality per session
- **Multi-turn conversations** — Full chat history maintained during session
- **Structured logging** — Console + rotating file logs, env-configurable
- **100% local option** — All LLM inference can run on your machine via Ollama

## Architecture

```
Streamlit UI ──HTTP──▶ FastAPI API ──▶ Chat Service ──▶ LangGraph Agent
                                                            │
                                                      ┌─────┴─────┐
                                                 Tool Calls    LLM Calls
                                                 (DuckDuckGo)  (Local / Groq)
```

| Layer | Package | Key Modules |
|-------|---------|-------------|
| UI | `src/ui/` | `chat.py` — Streamlit chat interface |
| API | `src/api/` | `app.py` — FastAPI factory, `routes.py` — endpoints, `schemas.py` — models |
| Core | `src/core/` | `chat.py` — chat service, `agent.py` — LangGraph ReAct agent, `tools.py` — tool registry |
| Common | `src/common/` | `config.py` — settings & model registry, `logger.py` — logging |
| Infra | `docker/` | Docker Compose (Ollama + LiteLLM) |

## Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose *(for local models only)*
- NVIDIA GPU + drivers *(optional, for faster local inference)*
- Groq API key *(optional, for cloud models)*

### 1. Set up environment

```bash
git clone <repository-url>
cd chat
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env — add your GROQ_API_KEY for cloud models
```

### 3. Start LLM infrastructure (optional — for local models)

```bash
cd docker
docker compose up -d
# Wait for models to download (~5–10 min first time)
docker compose logs -f model-puller
cd ..
```

### 4. Launch the app

```bash
# Terminal 1 — API backend
uvicorn src.api.app:app --reload

# Terminal 2 — Streamlit UI
streamlit run src/ui/chat.py
```

- **Chat UI:** `http://localhost:8501`
- **API docs:** `http://localhost:8000/docs`

## Available Models

| Model | Provider | ID | Notes |
|-------|----------|-----|-------|
| Phi-3 | Local | `phi3` | Default model, lightweight |
| Gemma 2B | Local | `gemma:2b` | Google's compact model |
| Mistral | Local | `mistral` | Strong general-purpose model |
| GPT-4 Turbo | Local | `gpt-4-turbo` | Mapped to Llama3 locally |
| Qwen3 4B | Local | `qwen3` | Alibaba's multilingual model |
| Groq GPT-OSS 120B | Groq | `openai/gpt-oss-120b` | Large cloud model |
| Groq Llama 3.1 70B | Groq | `llama-3.1-70b-versatile` | Fast cloud model |
| Groq Llama 3.1 8B | Groq | `llama-3.1-8b-instant` | Fastest cloud model |
| Groq Mixtral 8x7B | Groq | `mixtral-8x7b-32768` | MoE architecture |

## Project Structure

```
chat/
├── src/
│   ├── common/              # Shared utilities
│   │   ├── config.py        # Env settings, model registry, model factory
│   │   └── logger.py        # Rotating file + console logging
│   ├── core/                # Business logic
│   │   ├── agent.py         # LangGraph ReAct agent + callback logger
│   │   ├── chat.py          # Public chat service interface
│   │   └── tools.py         # Tool definitions (web search)
│   ├── api/                 # FastAPI REST layer
│   │   ├── app.py           # Application factory + middleware
│   │   ├── routes.py        # Endpoint handlers
│   │   └── schemas.py       # Request/response Pydantic models
│   └── ui/                  # Streamlit frontend
│       └── chat.py          # Chat UI (entry point)
├── docker/
│   ├── config.yaml          # LiteLLM model routing
│   └── docker-compose.yml   # Ollama + LiteLLM services
├── tests/                   # Test suite (empty — not yet implemented)
├── docs/                    # Project documentation
├── logs/                    # Log files (auto-created, git-ignored)
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── README.md
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENAI_ENDPOINT` | `http://localhost:4000/` | LiteLLM proxy URL |
| `OPENAI_API_KEY` | `my-secret-key` | LiteLLM API key |
| `GROQ_API_KEY` | *(empty)* | Groq cloud API key |
| `FASTAPI_URL` | `http://localhost:8000` | Backend URL for Streamlit |
| `LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `LOG_FILE` | `logs/app.log` | Log file path |
| `LOG_MAX_MB` | `10` | Max log file size (MB) before rotation |
| `LOG_BACKUPS` | `5` | Number of rotated log backups |

## Adding a New Model

1. Add the model pull command in `docker/docker-compose.yml` → `model-puller` service *(local only)*
2. Add model routing in `docker/config.yaml` → `model_list` *(local only)*
3. Register display name + provider in `src/common/config.py` → `AVAILABLE_MODELS`
4. Add the env var to `.env.example`

## Adding a New Tool

1. Define the tool in `src/core/tools.py`
2. Add it to the `ALL_TOOLS` list
3. The agent will automatically discover and use it when appropriate

## Documentation

Full project documentation is available in the [`docs/`](docs/) folder:

- [Documentation Index](docs/index.md)
- [Project Overview](docs/project-overview.md)
- [Architecture](docs/architecture.md)
- [Source Tree Analysis](docs/source-tree-analysis.md)
- [Development Guide](docs/development-guide.md)

## License

_No license specified._
