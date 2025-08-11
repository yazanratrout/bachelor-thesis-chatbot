import streamlit as st
import sys
import os
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

from backend.chatbot import (
    answer_question,
    set_active_model,
    get_active_model,
    MODEL_REGISTRY,
)

st.set_page_config(page_title="Thesis Chatbot", layout="centered")

st.sidebar.subheader("Settings")
model_keys = list(MODEL_REGISTRY.keys())
current_model = get_active_model() or "all-MiniLM-L6-v2"
try:
    default_idx = model_keys.index(current_model)
except ValueError:
    default_idx = 0

selected_model = st.sidebar.selectbox("Embedding model", model_keys, index=default_idx)
top_k = st.sidebar.slider("Top-k candidates", min_value=1, max_value=10, value=5, step=1)
use_reranker = st.sidebar.checkbox("Use reranker", value=True)
show_score = st.sidebar.checkbox("Show similarity score", value=False)

# Apply model switch
if selected_model != get_active_model():
    with st.spinner(f"Loading model: {selected_model}"):
        set_active_model(selected_model)

st.title("Your IRC Assistant")
st.markdown("Chat with your document-based assistant below.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pending_bot_response" not in st.session_state:
    st.session_state.pending_bot_response = None

user_input = st.chat_input("How can I help you today?")
if user_input:
    st.session_state.chat_history.append({"role": "user", "message": user_input})
    st.session_state.pending_bot_response = answer_question(user_input, top_k=top_k, use_reranker=use_reranker)

for chat in st.session_state.chat_history:
    role = "user" if chat["role"] in ("user",) else "assistant"
    avatar = "👤" if role == "user" else "🤖"
    with st.chat_message(role, avatar=avatar):
        st.markdown(chat["message"])
        if role == "assistant" and chat.get("meta"):
            meta = chat["meta"]
            source = meta.get("source")
            score = meta.get("score")
            if source:
                st.caption(f"Source: {source}")
            if show_score and score is not None:
                try:
                    st.caption(f"Similarity: {float(score):.3f}")
                except Exception:
                    pass
    time.sleep(0.3)

if st.session_state.pending_bot_response:
    res = st.session_state.pending_bot_response  # dict {text, source, score}

    with st.chat_message("assistant", avatar=os.path.join(parent_dir, "icons//bot1.jpg")):
        typing_placeholder = st.empty()
        typing_placeholder.markdown("Typing...")
        time.sleep(0.5)
        typing_placeholder.markdown(res["text"])
        # Meta caption(s)
        if res.get("source"):
            st.caption(f"Source: {res['source']}")
        if show_score and (res.get("score") is not None):
            try:
                st.caption(f"Similarity: {float(res['score']):.3f}")
            except Exception:
                pass

    # Persist to history
    st.session_state.chat_history.append({
        "role": "assistant",
        "message": res["text"],
        "meta": {"source": res.get("source"), "score": res.get("score")}
    })
    st.session_state.pending_bot_response = None

st.markdown("""
<style>
#chat-warning {
    position: fixed;
    bottom: 0.5rem;
    left: 50%;
    transform: translateX(-50%);
    font-size: 0.88rem;
    padding: 4px 10px;
    z-index: 999;
}
</style>
<div id="chat-warning">
    The chatbot has no memory yet. Please don't ask follow-up questions.
</div>
""", unsafe_allow_html=True)