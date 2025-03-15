import sys
import os
import json
import streamlit as st
from neo4j import GraphDatabase
import google.generativeai as genai

# ✅ Ensure imports work by setting correct paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ Load secrets safely
NEO4J_URI = st.secrets["neo4j"]["uri"]
NEO4J_USER = st.secrets["neo4j"]["user"]
NEO4J_PASSWORD = st.secrets["neo4j"]["password"]
GEMINI_API_KEY = st.secrets["gemini"]["api_key"]

# ✅ Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

class Chatbot:
    def __init__(self):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self):
        """Close Neo4j connection"""
        self.driver.close()

    def chat(self, user_input: str):
        """
        Process user query, retrieve knowledge from Neo4j, and generate chatbot response.
        """
        text_chunks = self._find_relevant_text(user_input)
        structured_data = {
            "query": user_input,
            "text_chunks": text_chunks
        }

        return self._generate_gemini_response(user_input, structured_data)

    def _find_relevant_text(self, query_text: str):
        """
        Query Neo4j for relevant text chunks based on user input.
        """
        query = """
        MATCH (c:TextChunk)
        WHERE toLower(c.text) CONTAINS toLower($query_text)
        RETURN c.text AS text
        LIMIT 5
        """
        with self.driver.session() as session:
            results = session.run(query, query_text=query_text)
            return [record["text"] for record in results]

    def _generate_gemini_response(self, user_input: str, structured_data):
        """
        Generate chatbot response using Gemini LLM.
        """
        prompt = f"""
        You are a chatbot that answers user queries based on uploaded documents.
        
        User's Query: {user_input}

        Knowledge Graph Data:
        {json.dumps(structured_data, indent=2)}

        Provide a user-friendly response based on the available information.
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        return response.text if response else "⚠️ No relevant information found."

