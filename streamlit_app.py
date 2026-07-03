# Strict sqlite3 override for Streamlit Cloud
import os
import sys
try:
    import pysqlite3
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

# Verify sqlite3 version (helpful for debugging Streamlit logs)
import sqlite3
print(f"Loaded sqlite3 version: {sqlite3.sqlite_version}")
if sqlite3.sqlite_version_info < (3, 35, 0):
    print("WARNING: sqlite3 version is below 3.35.0, ChromaDB may fail!")

import streamlit as st
import sys
import os

# Ensure the backend module can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.chat_flow import process_chat_message
from backend.core.rag_pipeline import get_rag_pipeline

@st.cache_resource
def load_rag_pipeline():
    """Warms up the RAG pipeline once per app lifecycle."""
    return get_rag_pipeline()

# Initialize pipeline in background
_ = load_rag_pipeline()

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

# Sidebar with supported funds
with st.sidebar:
    st.header("Supported Funds")
    st.write("I currently have knowledge about the following mutual funds:")
    
    import json
    sources_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "ingestion", "sources.json")
    try:
        with open(sources_path, "r") as f:
            sources_data = json.load(f)
            
        for amc in sources_data.get("sources", []):
            with st.expander(amc["amc"]):
                for scheme in amc["schemes"]:
                    st.markdown(f"- [{scheme['name']}]({scheme['url']})")
    except Exception as e:
        st.error("Unable to load fund list.")

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
                import traceback
                tb = traceback.format_exc()
                _logger.error(f"Error processing query: {e}\n{tb}")
                error_msg = f"I encountered an error while trying to process your request:\n\n```\n{e}\n\n{tb}\n```"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
