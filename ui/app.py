import streamlit as st
import sys
import os
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

from backend.chatbot import answer_question

st.set_page_config(page_title="Thesis Chatbot", layout="centered")

st.title("Your IRC Assistant")
st.markdown("Chat with your document-based assistant below.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pending_bot_response" not in st.session_state:
    st.session_state.pending_bot_response = None

user_input = st.chat_input("How can I help you today?")
if user_input:
    st.session_state.chat_history.append({"role": "user", "message": user_input})
    st.session_state.pending_bot_response = answer_question(user_input)

for chat in st.session_state.chat_history:
    with st.chat_message("user" if chat["role"] == "user" else "assistant", avatar="👤" if chat["role"] == "user" else "🤖"):
        st.markdown(chat["message"])
    time.sleep(0.3)
    
if st.session_state.pending_bot_response:
    with st.chat_message("assistant", avatar=os.path.join(parent_dir, "icons//bot1.jpg")):
        typing_placeholder = st.empty()
        typing_placeholder.markdown("Typing...")
        time.sleep(0.5)
        typing_placeholder.markdown(st.session_state.pending_bot_response)
    
    st.session_state.chat_history.append({"role": "bot", "message": st.session_state.pending_bot_response})
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