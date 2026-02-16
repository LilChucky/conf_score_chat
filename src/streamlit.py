"""
Streamlit Chat UI — generic AI chat interface backed by local Ollama models.
Run with:  streamlit run src/streamlit.py
"""

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from config import AVAILABLE_MODELS, DEFAULT_MODEL
from app import chat

# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="AI Chat", page_icon="💬", layout="centered")
st.title("💬 AI Chat")

# ── Sidebar: model picker + settings ────────────────────────
with st.sidebar:
    st.header("Settings")
    selected_model = st.selectbox("Model", list(AVAILABLE_MODELS.keys()), index=list(AVAILABLE_MODELS.keys()).index(DEFAULT_MODEL))
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
    system_prompt = st.text_area("System Prompt", value="You are a helpful assistant.", height=100)

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ── Chat history (session state) ─────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing messages
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# ── User input ───────────────────────────────────────────────
if prompt := st.chat_input("Type your message…"):
    # Add user message
    user_msg = HumanMessage(content=prompt)
    st.session_state.messages.append(user_msg)
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build full message list (system prompt + history)
    full_messages = [SystemMessage(content=system_prompt)] + st.session_state.messages

    # Get LLM response
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            response = chat(full_messages, model_name=selected_model, temperature=temperature)
        st.markdown(response.content)

    # Store assistant response
    st.session_state.messages.append(response)
