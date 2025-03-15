import streamlit as st
from query_engine import Chatbot
from document_processor import DocumentProcessor

# ✅ Load secrets from Streamlit
NEO4J_URI = st.secrets["neo4j"]["uri"]
NEO4J_USER = st.secrets["neo4j"]["user"]
NEO4J_PASSWORD = st.secrets["neo4j"]["password"]

# ✅ Initialize chatbot & document processor
chatbot = Chatbot(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)
processor = DocumentProcessor(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)

st.title("Knowledge Graph Chatbot")

# 📂 File Upload Section
st.subheader("📂 Upload a Document to Add to Knowledge Graph")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file:
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
