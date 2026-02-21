# Chat — Documentation Index

> Generated on 2026-02-16 | Quick Scan | Monolith (backend)

## Project Overview

- **Type:** Monolith (single cohesive codebase)
- **Primary Language:** Python
- **Architecture:** Layered (Streamlit UI → LangChain Backend → LiteLLM/Ollama)
- **Entry Point:** `streamlit run src/streamlit.py`

## Quick Reference

| Property          | Value                                          |
| ----------------- | ---------------------------------------------- |
| Tech Stack        | Python, Streamlit, LangChain, LiteLLM, Ollama |
| Entry Point       | `streamlit run src/streamlit.py`               |
| Infrastructure    | `cd docker && docker compose up -d`            |
| Architecture      | Layered (Config → Backend → UI)                |
| Models Available  | Phi-3, Gemma 2B, Mistral, GPT-4 Turbo, Qwen3  |

## Generated Documentation

- [Project Overview](./project-overview.md)
- [Architecture](./architecture.md)
- [Source Tree Analysis](./source-tree-analysis.md)
- [Development Guide](./development-guide.md)
- [API Contracts](./api-contracts.md) _(To be generated)_
- [Data Models](./data-models.md) _(To be generated)_
- [Deployment Guide](./deployment-guide.md) _(To be generated)_

## Getting Started

1. Clone the repo and create a Python virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`
4. Start LLM infrastructure: `cd docker && docker compose up -d`
5. Launch the app: `streamlit run src/streamlit.py`

See [Development Guide](./development-guide.md) for full details.
