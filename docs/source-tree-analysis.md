# Source Tree Analysis — Chat

## Directory Structure

```
chat/
├── .env                    # Environment variables (git-ignored)
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules (.env, __pycache__, .vscode/)
├── README.md               # Project README
│
├── src/                    # ⭐ Application source code
│   ├── __init__.py         # Python package marker (empty)
│   ├── app.py              # ⭐ Core chat logic — get_llm(), chat()
│   ├── config.py           # ⭐ Centralized configuration — LLMConfig, models registry
│   └── streamlit.py        # ⭐ Streamlit UI — chat interface (ENTRY POINT)
│
├── tests/                  # Test directory (empty — no tests yet)
│
├── docker/                 # ⭐ Infrastructure configuration
│   ├── config.yaml         # LiteLLM proxy model routing
│   └── docker-compose.yml  # Ollama + LiteLLM + Model Puller services
│
├── docs/                   # Generated project documentation
│
├── _bmad/                  # BMAD framework (project tooling — not part of app)
│   ├── _config/            # BMAD manifests and agent configurations
│   ├── _memory/            # BMAD agent memory/sidecar files
│   ├── bmm/                # BMAD Method Module (agents, workflows)
│   ├── bmb/                # BMAD Builder Module
│   ├── cis/                # Creative & Innovation Suite
│   ├── core/               # BMAD Core
│   └── tea/                # Test Architect Module
│
├── _bmad-output/           # BMAD workflow outputs
│   ├── bmb-creations/
│   ├── implementation-artifacts/
│   ├── planning-artifacts/
│   └── test-artifacts/
│
└── .github/
    └── agents/             # BMAD GitHub Copilot agent definitions
```

## Critical Folders

| Folder     | Purpose                                          | Key Files                                 |
| ---------- | ------------------------------------------------ | ----------------------------------------- |
| `src/`     | All application source code                      | `app.py`, `config.py`, `streamlit.py`     |
| `docker/`  | Docker infrastructure for LLM services           | `docker-compose.yml`, `config.yaml`       |
| `tests/`   | Test directory (currently empty)                 | —                                         |
| `docs/`    | Generated documentation                          | `project-overview.md`, `architecture.md`  |

## Entry Points

| Entry Point                       | Purpose                | Notes                         |
| --------------------------------- | ---------------------- | ----------------------------- |
| `streamlit run src/streamlit.py`  | Launch the chat UI     | Main application entry point  |
| `python src/app.py`               | Run smoke test         | Quick LLM connectivity check  |
| `docker compose -f docker/docker-compose.yml up` | Start infrastructure | Ollama + LiteLLM |

## Import Dependency Graph

```
streamlit.py
├── config.AVAILABLE_MODELS, DEFAULT_MODEL
├── app.chat
│   ├── config.llm_config, AVAILABLE_MODELS, DEFAULT_MODEL
│   └── langchain_openai.ChatOpenAI
└── langchain_core.messages (HumanMessage, AIMessage, SystemMessage)
```
