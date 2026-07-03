import streamlit as st
import sys
import os

# Ensure the backend module can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.chat_flow import process_chat_message

st.set_page_config(page_title="Mutual Fund FAQ Assistant", page_icon="📈", layout="centered")

st.title("Mutual Fund FAQ Assistant 📈")
st.caption("Facts-only. No investment advice. Based on Groww Mutual Fund data.")

# Validate API Key
from backend.config import settings
import logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger("streamlit_app")

_logger.info(f"GROQ_API_KEY loaded: {'Yes' if settings.GROQ_API_KEY else 'No'} (len={len(settings.GROQ_API_KEY) if settings.GROQ_API_KEY else 0})")
_logger.info(f"CHROMA_PERSIST_DIR: {settings.CHROMA_PERSIST_DIR}")
_logger.info(f"EMBEDDING_MODEL: {settings.EMBEDDING_MODEL}")

if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_key_here":
    st.error("⚠️ GROQ_API_KEY is missing! If you are deploying on Streamlit Cloud, please add it to your App Settings -> Secrets.")
    st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add welcome message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hi! I'm your Mutual Fund FAQ Assistant. I can answer factual questions about 15 selected schemes from AMCs like Nippon India, Motilal Oswal, Mirae Asset, ABSL, and ICICI Prudential. What would you like to know?"
    })

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle suggested questions when chat is empty (only welcome message)
suggested_question = None
if len(st.session_state.messages) == 1:
    st.write("**Try asking:**")
    q1 = "What is the expense ratio of Nippon India Small Cap Fund?"
    q2 = "What is the exit load for ICICI Prudential Balanced Advantage Fund?"
    q3 = "What is the minimum SIP amount for Mirae Asset Flexi Cap Fund?"
    
    if st.button(q1, use_container_width=True):
        suggested_question = q1
    if st.button(q2, use_container_width=True):
        suggested_question = q2
    if st.button(q3, use_container_width=True):
        suggested_question = q3

# React to user input or suggested question
prompt = st.chat_input("Ask a question about a mutual fund scheme...")
if suggested_question:
    prompt = suggested_question

if prompt:
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Searching mutual fund documents..."):
            try:
                response = process_chat_message(prompt)
                
                answer = response.get("answer", "")
                citation = response.get("citation")
                last_updated = response.get("last_updated")
                
                # Format the display text
                display_text = answer
                if citation:
                    display_text += f"\n\n**Source:** [{citation['title']}]({citation['url']})"
                if last_updated:
                    display_text += f"\n\n*Last updated: {last_updated}*"
                
                st.markdown(display_text)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": display_text})
            except Exception as e:
                error_msg = f"Sorry, an error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
