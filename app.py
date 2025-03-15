import streamlit as st
from query_engine import Chatbot
from document_processor import DocumentProcessor

# ✅ Load Neo4j Credentials from Streamlit Secrets
import os

NEO4J_URI = os.getenv("NEO4J_URI", st.secrets["NEO4J_URI"])
NEO4J_USER = os.getenv("NEO4J_USER", st.secrets["NEO4J_USER"])
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", st.secrets["NEO4J_PASSWORD"])

# ✅ Initialize Neo4j Chatbot & Document Processor
chatbot = Chatbot(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)
processor = DocumentProcessor(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)

# ✅ Streamlit UI Title
st.title("📚 Knowledge Graph Chatbot")

# ✅ File Upload Section
st.header("Upload a Document to Add to Knowledge Graph")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file:
    st.write("📂 Processing file...")
    
    # ✅ Save file temporarily
    temp_file_path = f"/tmp/{uploaded_file.name}"
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # ✅ Process PDF & store in Neo4j
    try:
        processor.process_pdf(temp_file_path)
        st.success("✅ File processed successfully! Knowledge Graph updated.")
    except Exception as e:
        st.error(f"⚠️ Error processing document: {e}")

# ✅ Chatbot Query Input
st.header("💬 Ask the Chatbot")
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
                if isinstance(chunk, str):  # ✅ Ensure chunk is a string
                    full_response += chunk  
                elif hasattr(chunk, "text"):  # ✅ If chunk is an object, extract its text
                    full_response += chunk.text  
                else:
                    print(f"⚠️ Unexpected chunk format: {chunk}")  # Debugging message
                
                response_placeholder.write(full_response)  # ✅ Update UI dynamically
