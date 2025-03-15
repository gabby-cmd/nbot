import streamlit as st
from query_engine import Chatbot
from document_processor import DocumentProcessor

# Initialize chatbot
chatbot = Chatbot()
processor = DocumentProcessor()

st.title("📚 Knowledge Graph Chatbot")

### **🔹 Upload and Process Documents**
st.sidebar.header("📂 Upload a Document")
uploaded_file = st.sidebar.file_uploader("Upload a document", type=["pdf", "txt", "docx"])

if uploaded_file:
    with st.spinner("Processing document... ⏳"):
        processor.process_document(uploaded_file)
        st.sidebar.success("✅ Document processed and stored in Neo4j!")

### **🔹 Chatbot Interface**
st.header("🤖 Chat with the Knowledge Graph")

user_input = st.text_input("Ask a question:")
if st.button("Send"):
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            response_stream = chatbot.chat(user_input)  # Call chatbot
            response_placeholder = st.empty()  # Placeholder for streamed text
            full_response = ""

            for chunk in response_stream:
                full_response += chunk.text  # Append streamed text
                response_placeholder.write(full_response)  # Update UI dynamically
