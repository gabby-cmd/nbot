import streamlit as st
import os
from query_engine import Chatbot
from document_processor import DocumentProcessor

# ✅ Load Neo4j credentials from Streamlit secrets
URI = st.secrets["neo4j"]["uri"]
USER = st.secrets["neo4j"]["user"]
PASSWORD = st.secrets["neo4j"]["password"]

# ✅ Initialize document processor
processor = DocumentProcessor(uri=URI, user=USER, password=PASSWORD)

# ✅ Initialize chatbot
chatbot = Chatbot()

st.title("📚 Knowledge Graph Chatbot")

### **🔹 Upload and Process Documents**
st.sidebar.header("📂 Upload a Document")
uploaded_file = st.sidebar.file_uploader("Upload a PDF document", type=["pdf"])

if uploaded_file:
    with st.spinner("Processing document... ⏳"):
        try:
            # ✅ Ensure 'uploads' folder exists
            os.makedirs("uploads", exist_ok=True)

            # ✅ Save uploaded file locally
            file_path = os.path.join("uploads", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # ✅ Process PDF and store chunks in Neo4j
            processor.process_pdf(file_path)

            st.sidebar.success("✅ Document processed and stored in Neo4j!")

        except Exception as e:
            st.error(f"🚨 Error processing document: {e}")

### **🔹 Chatbot Interface**
st.header("🤖 Chat with the Knowledge Graph")

user_input = st.text_input("Ask a question:")
