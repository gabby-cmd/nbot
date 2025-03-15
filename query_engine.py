import google.generativeai as genai
from neo4j import GraphDatabase
import streamlit as st
import json

# Configure Gemini API
genai.configure(api_key=st.secrets["gemini"]["api_key"])

class Chatbot:
    def __init__(self, uri, user, password, database="neo4j"):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        """Close Neo4j connection"""
        self.driver.close()

    def chat(self, user_input):
        """Retrieve relevant data and generate chatbot response"""
        text_chunks = self._find_relevant_text(user_input)

        if not text_chunks:
            return ["⚠️ No relevant information found in the knowledge graph. Try another query."]

        structured_data = {
            "query": user_input,
            "text_chunks": text_chunks
        }

        return self._generate_gemini_response(user_input, structured_data)

    def _find_relevant_text(self, query_text):
        """Find relevant text chunks from Neo4j"""
        query = """
        MATCH (c:TextChunk)
        WHERE toLower(c.text) CONTAINS toLower($query_text)
        RETURN c.text AS text
        """

        with self.driver.session() as session:
            try:
                results = session.run(query, {"query_text": query_text})  # ✅ Fixed query syntax
                return [record["text"] for record in results]
            except Exception as e:
                print(f"❌ Query Execution Failed: {e}")
                return []

    def _generate_gemini_response(self, user_input, structured_data):
        """Generate chatbot response using Gemini LLM"""
        prompt = f"""
        You are a chatbot that answers user queries based on structured knowledge.

        User's Query: {user_input}

        Knowledge Graph Data:
        {json.dumps(structured_data, indent=2)}

        Provide a conversational, user-friendly response explaining the answer in simple terms.
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response_stream = model.generate_content_stream(prompt)  # ✅ Streams response

        return response_stream  # ✅ Returns a streaming generator
