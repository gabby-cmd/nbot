import streamlit as st
import os
from query_engine import Chatbot
from document_processor import DocumentProcessor

# Load Neo4j and Gemini API credentials from Streamlit Secrets
NEO4J_URI = st.secrets["neo4j"]["uri"]
NEO4J_USER = st.secrets["neo4j"]["user"]
NEO4J_PASSWORD = st.secrets["neo4j"]["password"]
GEMINI_API_KEY = st.secrets["gemini"]["api_key"]

# Initialize Neo4j document processor and chatbot
processor = DocumentProcessor(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)
chatbot = Chatbot(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)

st.title("📚 Knowledge Graph Chatbot")

# **📂 Upload Document Section**
st.header("📂 Upload a Document to Add to Knowledge Graph")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file:
    with st.spinner("🔄 Processing file..."):
        file_path = f"/tmp/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        processor.process_pdf(file_path)  # ✅ Process and store in Neo4j
        st.success("✅ File processed successfully! Knowledge Graph updated.")

# **💬 Chatbot Interaction Section**
st.header("💬 Ask the Chatbot")
user_input = st.text_input("Ask a question about the uploaded document:")

if st.button("Send"):
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            response_stream = chatbot.chat(user_input)  # ✅ Call chatbot
            
            for chunk in response_stream:
                if isinstance(chunk, str):  # ✅ Ensure chunk is a string
                    full_response += chunk
                    response_placeholder.write(full_response)  # ✅ Update UI dynamically
                else:
                    print(f"Unexpected chunk format: {chunk}")  # Debugging
