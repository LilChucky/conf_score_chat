# Project Overview — Chat

## Executive Summary

**Chat** is a local AI chat application that provides a conversational interface powered by locally-hosted large language models (LLMs). It uses **Streamlit** for the UI, **LangChain** for LLM orchestration, and **Ollama + LiteLLM** as the model serving infrastructure — all running via Docker Compose.

The application lets users select from multiple LLM models (Phi-3, Gemma 2B, Mistral, GPT-4 Turbo, Qwen3 4B), adjust response temperature, set a system prompt, and have multi-turn conversations — all without sending data to external APIs.

## Key Facts

| Property             | Value                                      |
| -------------------- | ------------------------------------------ |
| **Project Name**     | Chat                                       |
| **Type**             | Monolith (single cohesive codebase)        |
| **Primary Language** | Python                                     |
| **UI Framework**     | Streamlit                                  |
| **LLM Framework**    | LangChain (`langchain_openai`)             |
| **LLM Proxy**        | LiteLLM (OpenAI-compatible API proxy)      |
| **LLM Runtime**      | Ollama (local model hosting)               |
| **Architecture**     | Layered: Config → Backend → Streamlit UI   |
| **Containerization** | Docker Compose                             |
| **Entry Point**      | `streamlit run src/streamlit.py`           |

## Technology Stack

| Category         | Technology                       | Purpose                            |
| ---------------- | -------------------------------- | ---------------------------------- |
| Language          | Python 3.x                      | Primary language                   |
| UI Framework      | Streamlit                        | Chat interface                     |
| LLM Framework     | LangChain (langchain_openai)     | LLM orchestration & messaging     |
| LLM Proxy         | LiteLLM                          | OpenAI-compatible proxy            |
| LLM Runtime       | Ollama                           | Local model hosting                |
| Config Validation  | Pydantic                         | Configuration schema validation    |
| Env Management     | python-dotenv                    | `.env` file loading                |
| Containerization   | Docker / Docker Compose          | Infrastructure orchestration       |

### Available Models

| Display Name   | Model ID       | Served By |
| -------------- | -------------- | --------- |
| Phi-3          | `phi3`         | Ollama    |
| Gemma 2B       | `gemma:2b`     | Ollama    |
| Mistral        | `mistral`      | Ollama    |
| GPT-4 Turbo    | `gpt-4-turbo`  | Ollama (llama3) |
| Qwen3 4B       | `qwen3`        | Ollama    |

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│              Streamlit UI (streamlit.py)         │
│  ┌─────────┐ ┌───────────┐ ┌─────────────────┐  │
│  │ Model   │ │Temperature│ │ System Prompt   │  │
│  │ Picker  │ │ Slider    │ │ Text Area       │  │
│  └─────────┘ └───────────┘ └─────────────────┘  │
│  ┌─────────────────────────────────────────────┐ │
│  │           Chat Message Area                 │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────┘
                       │ chat(messages, model, temp)
                       ▼
┌─────────────────────────────────────────────────┐
│            Backend Logic (app.py)                │
│  get_llm() → ChatOpenAI instance                │
│  chat()    → Invoke LLM, return AIMessage       │
└──────────────────────┬──────────────────────────┘
                       │ OpenAI-compatible API call
                       ▼
┌─────────────────────────────────────────────────┐
│         Configuration (config.py)               │
│  LLMConfig (Pydantic) — base_url, api_key       │
│  AVAILABLE_MODELS registry                       │
│  Loads from .env                                 │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│     Docker Infrastructure (docker-compose.yml)  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │  Ollama  │◄─│ Model    │  │   LiteLLM    │  │
│  │ :11434   │  │ Puller   │  │  Proxy :4000 │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│                   rag_net (bridge network)       │
└─────────────────────────────────────────────────┘
```

## Future Capabilities (Commented Out)

The Docker Compose file includes commented-out services for future RAG (Retrieval-Augmented Generation) capabilities:

- **Chroma DB** — Vector storage for embeddings (port 8000)
- **Neo4j** — Graph database storage (ports 7474, 7687)
