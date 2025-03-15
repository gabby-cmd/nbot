import streamlit as st
from query_engine import Chatbot

#  Import DocumentProcessor correctly
try:
    from document_processor import DocumentProcessor
    processor = DocumentProcessor()  #  Initialize processor
except ImportError as e:
    st.error(f"Failed to import DocumentProcessor: {e}")

#  Initialize chatbot
chatbot = Chatbot()

st.title("Knowledge Graph Chatbot")

### **🔹 Upload and Process Documents**
st.sidebar.header("📂 Upload a Document")
uploaded_file = st.sidebar.file_uploader("Upload a document", type=["pdf", "txt", "docx"])

if uploaded_file:
    with st.spinner("Processing document... ⏳"):
        try:
            #  Process document safely
            text_chunks, entities, relationships = processor.process_document(uploaded_file)
            
            # 🔍 Show extracted data for debugging
            st.sidebar.subheader("Extracted Data")
            st.sidebar.write("Text Chunks:", text_chunks)
            st.sidebar.write("Entities:", entities)
            st.sidebar.write("Relationships:", relationships)

            st.sidebar.success("Document processed and stored in Neo4j!")
        except Exception as e:
            st.error(f" Error processing document: {e}")

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
