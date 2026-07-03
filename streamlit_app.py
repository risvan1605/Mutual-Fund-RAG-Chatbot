import streamlit as st
import sys
import os

# Ensure the backend module can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.chat_flow import process_chat_message

st.set_page_config(page_title="Mutual Fund FAQ Assistant", page_icon="📈", layout="centered")

st.title("Mutual Fund FAQ Assistant 📈")
st.caption("Facts-only. No investment advice. Based on Groww Mutual Fund data.")

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

# React to user input
if prompt := st.chat_input("Ask a question about a mutual fund scheme..."):
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
