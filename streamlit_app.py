import streamlit as st
import uuid
from switch_model import get_answer

st.set_page_config(page_title="Unified Q&A Chatbot", page_icon="🤖")
st.title("🤖 Unified Q&A Chatbot")

# Unique session per user
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Sidebar model selection
st.sidebar.header("Model Selection")
model_choice = st.sidebar.radio(
    "Choose a model:",
    ["chatgroq", "ollama"]
)

# UI chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask your question...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_answer(
                user_input,
                model_choice,
                st.session_state.session_id
            )
            st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
