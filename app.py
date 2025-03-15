import streamlit as st
from query_engine import Chatbot

# ✅ Initialize chatbot without parameters
chatbot = Chatbot()

st.title("Knowledge Graph Chatbot")

# 📂 File Upload Section
st.subheader("📂 Upload a Document to Add to Knowledge Graph")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file:
    from document_processor import DocumentProcessor

    processor = DocumentProcessor()
    
    with st.spinner("🔄 Processing file..."):
        processor.process_pdf(uploaded_file)

    st.success("✅ File processed successfully! Knowledge Graph updated.")

# 💬 Chat Section
st.subheader("💬 Ask the Chatbot")
user_input = st.text_input("Ask a question about the uploaded document:")

if st.button("Send"):
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            response_text = chatbot.chat(user_input)  # ✅ Call chatbot
            st.write(response_text)  # ✅ Display response
