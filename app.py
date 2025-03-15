import streamlit as st
from query_engine import Chatbot
from document_processor import DocumentProcessor
import os

# Load Neo4j credentials from Streamlit secrets
NEO4J_URI = st.secrets["neo4j"]["uri"]
NEO4J_USER = st.secrets["neo4j"]["user"]
NEO4J_PASSWORD = st.secrets["neo4j"]["password"]

# Initialize chatbot and document processor
chatbot = Chatbot(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)
processor = DocumentProcessor(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)

st.title("📚 AI-Powered Knowledge Graph Chatbot")

# **📂 Upload a Document Section**
st.header("📂 Upload a Document to Add to Knowledge Graph")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file:
    with st.spinner("🔄 Processing file..."):
        file_path = f"./{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            processor.process_pdf(file_path)  # ✅ Process & store in Neo4j
            st.success("✅ File processed successfully! Knowledge Graph updated.")
        except Exception as e:
            st.error(f"🚨 Error processing document: {e}")

# **💬 Chatbot Section**
st.header("💬 Ask the Chatbot")
user_input = st.text_input("Ask a question about the uploaded document:")

if st.button("Send"):
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            response_stream = chatbot.chat(user_input)  # ✅ Call chatbot
            response_placeholder = st.empty()  # ✅ Placeholder for streaming text
            full_response = ""

            for chunk in response_stream:
                if isinstance(chunk, str):  # ✅ Ensure chunk is a string
                    full_response += chunk  
                    response_placeholder.write(full_response)  # ✅ Update UI dynamically
                else:
                    print(f"Unexpected chunk format: {chunk}")  # Debugging log
