# Development Guide — Chat

## Prerequisites

- **Python 3.10+** (with type hint support for `float | None`)
- **Docker** and **Docker Compose** (for Ollama and LiteLLM services)
- **NVIDIA GPU + drivers** (optional, for GPU-accelerated inference)

## Getting Started

### 1. Clone and Set Up Environment

```bash
# Clone the repository
git clone <repository-url>
cd chat

# Create a virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env if needed (defaults work for local Docker setup)
```

Key variables:

| Variable           | Default                    | Description                  |
| ------------------ | -------------------------- | ---------------------------- |
| `OPENAI_ENDPOINT`  | `http://localhost:4000/`   | LiteLLM proxy URL            |
| `OPENAI_API_KEY`   | `my-secret-key`            | LiteLLM API key              |

### 4. Start LLM Infrastructure

```bash
cd docker
docker compose up -d
```

This starts:
- **Ollama** on port 11434 (LLM server)
- **LiteLLM Proxy** on port 4000 (OpenAI-compatible API)
- **Model Puller** that automatically downloads: llama3, all-minilm, phi3, gemma:2b, qwen3:4b

Wait for model downloads to complete (check logs with `docker compose logs -f model-puller`).

### 5. Run the Application

```bash
cd ..
streamlit run src/streamlit.py
```

The chat UI will open in your browser (typically `http://localhost:8501`).

### 6. Quick Smoke Test (Optional)

```bash
python src/app.py
```

This sends "What is the capital of France?" to the default model (Phi-3) and prints the response.

## Project Structure

```
src/
├── app.py         # Core chat logic (get_llm, chat functions)
├── config.py      # Configuration (LLMConfig, model registry)
└── streamlit.py   # Streamlit chat UI (entry point)
```

## Common Tasks

| Task                          | Command                                        |
| ----------------------------- | ---------------------------------------------- |
| Start infrastructure          | `cd docker && docker compose up -d`            |
| Stop infrastructure           | `cd docker && docker compose down`             |
| View Ollama logs              | `docker compose -f docker/docker-compose.yml logs -f ollama` |
| View LiteLLM logs             | `docker compose -f docker/docker-compose.yml logs -f litellm` |
| Run the chat app              | `streamlit run src/streamlit.py`               |
| Run smoke test                | `python src/app.py`                            |
| Check model availability      | `curl http://localhost:11434/api/tags`          |

## Adding a New Model

1. Add the model pull command in `docker/docker-compose.yml` under the `model-puller` service
2. Add the model routing in `docker/config.yaml` under `model_list`
3. Add the display name + deployment env var in `src/config.py` → `AVAILABLE_MODELS`
4. Add the env var to `.env.example`

## Testing

The `tests/` directory is currently empty. No test framework has been configured yet.

## Known Gaps

- **No CI/CD pipeline** — No automated builds or deployments
- **No persistent chat storage** — Conversations are lost on refresh
- **No authentication** — Streamlit UI is open to anyone with network access
