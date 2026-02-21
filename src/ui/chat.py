"""
Streamlit Chat UI — calls the FastAPI backend for AI responses.
Run with:  streamlit run src/ui/chat.py
Requires the FastAPI backend to be running:
    uvicorn src.api.app:app --reload
"""

import logging
import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

API_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")


def _fetch_models() -> tuple[list[str], str]:
    """Fetch available models and default from the API."""
    log.info("Fetching model list from %s/models", API_URL)
    try:
        resp = requests.get(f"{API_URL}/models", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        log.info("Received %d models, default=%s", len(data["models"]), data["default"])
        return data["models"], data["default"]
    except requests.exceptions.ConnectionError:
        log.error("Cannot connect to API at %s", API_URL)
        st.error("⚠️ Cannot reach the API. Start the backend with: `uvicorn src.api.app:app --reload`")
        return [], "Phi-3"


def _send_chat(messages: list[dict], model: str, temperature: float) -> str:
    """POST to /chat and return the assistant reply text."""
    log.info("Sending chat: model=%s, messages=%d, temperature=%.2f", model, len(messages), temperature)
    payload = {"messages": messages, "model": model, "temperature": temperature}
    resp = requests.post(f"{API_URL}/chat", json=payload, timeout=300)
    resp.raise_for_status()
    reply = resp.json()["content"]
    log.info("Received reply: %d chars", len(reply))
    return reply


# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="AI Chat", page_icon="💬", layout="centered")
st.title("💬 AI Chat")

# ── Load models from API ─────────────────────────────────────
model_list, default_model = _fetch_models()

# ── Sidebar: model picker + settings ────────────────────────
with st.sidebar:
    st.header("Settings")
    if model_list:
        default_idx = model_list.index(default_model) if default_model in model_list else 0
        selected_model = st.selectbox("Model", model_list, index=default_idx)
    else:
        selected_model = default_model
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
    system_prompt = st.text_area("System Prompt", value="You are a helpful assistant.", height=100)

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ── Chat history (session state) ─────────────────────────────
# Messages stored as plain dicts: {"role": "user"|"assistant", "content": "..."}
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── User input ───────────────────────────────────────────────
if prompt := st.chat_input("Type your message…"):
    # Add user message
    user_msg = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_msg)
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build full message list (system prompt + history)
    full_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    # Call FastAPI backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                reply = _send_chat(full_messages, model=selected_model, temperature=temperature)
            except requests.exceptions.HTTPError as exc:
                detail = exc.response.json().get('detail', str(exc))
                log.error("API HTTP error: %s", detail)
                reply = f"❌ API error: {detail}"
            except requests.exceptions.ConnectionError:
                log.error("Connection error when calling %s/chat", API_URL)
                reply = "❌ Could not connect to the backend. Is it running?"
        st.markdown(reply)

    # Store assistant response
    st.session_state.messages.append({"role": "assistant", "content": reply})
