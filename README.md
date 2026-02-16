# 💬 AI Chat

A local AI chat application powered by open-source LLMs, with a clean Streamlit interface and fully local infrastructure — no data leaves your machine.

## Features

- **Multi-model support** — Switch between Phi-3, Gemma 2B, Mistral, GPT-4 Turbo (via Llama3), and Qwen3 4B
- **Adjustable temperature** — Control response creativity with a slider (0.0–1.0)
- **Custom system prompts** — Set the assistant's personality per session
- **Multi-turn conversations** — Full chat history maintained during session
- **100% local** — All LLM inference runs on your machine via Ollama
- **OpenAI-compatible API** — LiteLLM proxy provides a familiar API interface

## Architecture

```
Streamlit UI  →  LangChain (ChatOpenAI)  →  LiteLLM Proxy (:4000)  →  Ollama (:11434)  →  Local LLM
```

| Layer           | Component       | File / Location              |
| --------------- | --------------- | ---------------------------- |
| UI              | Streamlit       | `src/streamlit.py`           |
| Backend         | LangChain       | `src/app.py`                 |
| Configuration   | Pydantic + .env | `src/config.py`              |
| Infrastructure  | Docker Compose  | `docker/docker-compose.yml`  |

## Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- NVIDIA GPU + drivers _(optional, for faster inference)_

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
# Edit .env if needed — defaults work for local Docker setup
```

### 3. Start LLM infrastructure

```bash
cd docker
docker compose up -d
# Wait for models to download (~5–10 min first time)
docker compose logs -f model-puller
```

### 4. Launch the app

```bash
cd ..
streamlit run src/streamlit.py
```

Open `http://localhost:8501` in your browser.

## Available Models

| Model        | ID             | Notes                                    |
| ------------ | -------------- | ---------------------------------------- |
| Phi-3        | `phi3`         | Default model, lightweight               |
| Gemma 2B     | `gemma:2b`     | Google's compact model                   |
| Mistral      | `mistral`      | Strong general-purpose model             |
| GPT-4 Turbo  | `gpt-4-turbo`  | Mapped to Llama3 locally                 |
| Qwen3 4B     | `qwen3`        | Alibaba's multilingual model             |

## Project Structure

```
chat/
├── src/
│   ├── app.py           # Core chat logic (get_llm, chat)
│   ├── config.py        # Settings, model registry, env loading
│   └── streamlit.py     # Streamlit chat UI (entry point)
├── docker/
│   ├── config.yaml      # LiteLLM model routing
│   └── docker-compose.yml  # Ollama + LiteLLM services
├── tests/               # (empty — tests not yet implemented)
├── docs/                # Generated project documentation
├── .env.example         # Environment variable template
└── README.md
```

## Environment Variables

| Variable            | Default                  | Description              |
| ------------------- | ------------------------ | ------------------------ |
| `OPENAI_ENDPOINT`   | `http://localhost:4000/` | LiteLLM proxy URL        |
| `OPENAI_API_KEY`    | `my-secret-key`          | LiteLLM API key          |
| `PHI3_DEPLOYMENT`   | `phi3`                   | Phi-3 model ID           |
| `GEMMA_DEPLOYMENT`  | `gemma:2b`               | Gemma model ID           |
| `MISTRAL_DEPLOYMENT`| `mistral`                | Mistral model ID         |
| `GPT_DEPLOYMENT`    | `gpt-4-turbo`            | GPT-4 Turbo model ID    |
| `QWEN_DEPLOYMENT`   | `qwen3`                  | Qwen3 model ID           |

## Adding a New Model

1. Add the model pull command in `docker/docker-compose.yml` → `model-puller` service
2. Add model routing in `docker/config.yaml` → `model_list`
3. Register display name + env var in `src/config.py` → `AVAILABLE_MODELS`
4. Add the env var to `.env.example`

## Documentation

Full project documentation is available in the [`docs/`](docs/) folder:

- [Documentation Index](docs/index.md)
- [Project Overview](docs/project-overview.md)
- [Architecture](docs/architecture.md)
- [Source Tree Analysis](docs/source-tree-analysis.md)
- [Development Guide](docs/development-guide.md)

## License

_No license specified._
