import google.generativeai as genai
from neo4j import GraphDatabase
import json
import os
import streamlit as st  # ✅ Import Streamlit to access secrets

# ✅ Load Gemini API Key securely
GEMINI_API_KEY = st.secrets["gemini"]["api_key"]
genai.configure(api_key=GEMINI_API_KEY)

class Chatbot:
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        """Close Neo4j connection"""
        self.driver.close()

    def chat(self, user_input: str):
        """Process user query, retrieve knowledge from Neo4j, and generate chatbot response"""
        text_chunks = self._find_relevant_text(user_input)

        if not text_chunks:
            return ["⚠️ No relevant information found in the knowledge graph. Try another query."]

        structured_data = {
            "query": user_input,
            "text_chunks": text_chunks
        }

        return self._generate_gemini_response(user_input, structured_data)

    def _find_relevant_text(self, query_text: str):
        """Retrieve relevant document chunks from Neo4j"""
        query = """
        MATCH (c:TextChunk)
        WHERE toLower(c.text) CONTAINS toLower($query)
        RETURN c.text AS text
        """
        with self.driver.session() as session:
            results = session.run(query, query=query_text)
            return [record["text"] for record in results]

    def _generate_gemini_response(self, user_input: str, structured_data):
        """Generate chatbot response using Gemini LLM"""
        prompt = f"""
        You are an AI assistant that answers user queries based on structured knowledge.

        User's Query: {user_input}

        Relevant Text Chunks from Knowledge Graph:
        {json.dumps(structured_data, indent=2)}

        Provide a conversational, user-friendly response explaining the answer in simple terms.
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        return response.text.split("\n")  # ✅ Return formatted response
