# Architecture — Chat

## 1. Executive Summary

Chat is a Python-based AI chat application with a layered architecture: a **Streamlit UI** layer communicates with a **backend logic** layer (LangChain), which connects to locally-hosted LLMs through a **LiteLLM proxy** backed by **Ollama**. All infrastructure runs in Docker containers.

## 2. Architecture Pattern

**Layered Architecture** with three distinct tiers:

1. **Presentation Layer** — `streamlit.py` (Streamlit chat UI)
2. **Application Layer** — `app.py` (LLM client creation and message orchestration)
3. **Configuration Layer** — `config.py` (centralized settings via Pydantic)
4. **Infrastructure Layer** — Docker Compose (Ollama + LiteLLM)

### Data Flow

```
User Input → Streamlit UI → chat() → ChatOpenAI.invoke() → LiteLLM Proxy → Ollama → LLM Model
                                                                                       │
User ← Streamlit UI ← AIMessage ← chat() ← ChatOpenAI response ← LiteLLM ← Ollama ◄──┘
```

## 3. Component Details

### 3.1 Streamlit UI (`src/streamlit.py`)

- **Responsibilities:** User interaction, chat history management (session state), model/temperature/system-prompt selection
- **Key patterns:**
  - `st.session_state.messages` — In-memory chat history (list of LangChain message objects)
  - Sidebar controls for model picker, temperature slider, system prompt
  - `st.chat_message()` for rendering conversation
- **Entry point:** `streamlit run src/streamlit.py`

### 3.2 Backend Logic (`src/app.py`)

- **Responsibilities:** LLM instance creation, message invocation
- **Key functions:**
  - `get_llm(model_name, temperature)` — Creates a `ChatOpenAI` instance configured for LiteLLM proxy
  - `chat(messages, model_name, temperature)` — Sends messages to LLM, returns `AIMessage`
- **Dependencies:** `langchain_openai.ChatOpenAI`, `config.py`

### 3.3 Configuration (`src/config.py`)

- **Responsibilities:** Load environment variables, define available models, provide singleton config
- **Key elements:**
  - `LLMConfig` (Pydantic BaseModel) — `base_url`, `api_key`, `default_temperature`
  - `AVAILABLE_MODELS` — Registry mapping display names to LiteLLM model identifiers
  - `DEFAULT_MODEL` — `"Phi-3"`
  - `llm_config` — Singleton instance

### 3.4 Docker Infrastructure (`docker/`)

- **`docker-compose.yml`** — Orchestrates:
  - **Ollama** (port 11434) — Local LLM server with GPU support (NVIDIA CDI)
  - **Model Puller** — Alpine/curl helper that pulls models on startup (llama3, all-minilm, phi3, gemma:2b, qwen3:4b)
  - **LiteLLM Proxy** (port 4000) — OpenAI-compatible API facade
- **`config.yaml`** — LiteLLM model routing configuration mapping model names to Ollama endpoints
- **Network:** `rag_net` (bridge)
- **Volumes:** `ollama_data` (persistent model storage)

## 4. Configuration Management

### Environment Variables (`.env`)

| Variable            | Default                       | Purpose                       |
| ------------------- | ----------------------------- | ----------------------------- |
| `OPENAI_ENDPOINT`   | `http://localhost:4000/`      | LiteLLM proxy URL             |
| `OPENAI_API_KEY`    | `my-secret-key`               | LiteLLM authentication key    |
| `PHI3_DEPLOYMENT`   | `phi3`                        | Phi-3 model identifier        |
| `GEMMA_DEPLOYMENT`  | `gemma:2b`                    | Gemma model identifier        |
| `MISTRAL_DEPLOYMENT`| `mistral`                     | Mistral model identifier      |
| `GPT_DEPLOYMENT`    | `gpt-4-turbo`                 | GPT-4 Turbo model identifier  |
| `QWEN_DEPLOYMENT`   | `qwen3`                       | Qwen3 model identifier        |

### LiteLLM Model Routing (`docker/config.yaml`)

Maps each model name to the corresponding Ollama model endpoint at `http://ollama:11434`.

## 5. State Management

- **Session-only** — Chat history lives in `st.session_state.messages` (Streamlit session state)
- **No persistent storage** — Conversations are lost on page refresh or session end
- **No database** — No data models, migrations, or ORM

## 6. Security Considerations

- LiteLLM proxy uses a static API key (`my-secret-key` by default)
- All traffic is local (Docker bridge network)
- No authentication on the Streamlit UI
- `.env` file excluded from Git via `.gitignore`

## 7. Testing

- `tests/` directory exists but is **empty**
- No test framework configured
- `app.py` includes a `__main__` smoke test

## 8. Deployment

- **Local development:** Docker Compose for infrastructure + `streamlit run` for the app
- **No CI/CD pipelines** configured
- **No production deployment** configuration
- GPU support available via NVIDIA CDI in Docker Compose
