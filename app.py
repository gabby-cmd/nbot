import streamlit as st
from query_engine import Chatbot

# Initialize chatbot
chatbot = Chatbot()

st.title("Knowledge Graph Chatbot")

#  Chat Input
user_input = st.text_input("Ask a question about the knowledge graph:")
if st.button("Send"):
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            response_stream = chatbot.chat(user_input)  # **Call chatbot**
            response_placeholder = st.empty()  # **Placeholder for streaming text**
            full_response = ""

            for chunk in response_stream:
                full_response += chunk.text  # **Append streamed text**
                response_placeholder.write(full_response)  # **Update UI dynamically**
