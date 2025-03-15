import google.generativeai as genai
from neo4j import GraphDatabase
import json
import streamlit as st

# Load secrets from Streamlit Cloud
NEO4J_URI = st.secrets["neo4j"]["uri"]
NEO4J_USER = st.secrets["neo4j"]["user"]
NEO4J_PASSWORD = st.secrets["neo4j"]["password"]
GEMINI_API_KEY = st.secrets["gemini"]["api_key"]

# Configure Gemini API
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

        structured_data = {
            "query": user_input,
            "text_chunks": text_chunks
        }

        # If no relevant information is found
        if not text_chunks:
            return "⚠️ No relevant information found in the knowledge graph. Try another query."

        return self._generate_gemini_response(user_input, structured_data)

    def _find_relevant_text(self, query_text: str):
        """Find relevant text chunks from Neo4j"""
        query = """
        MATCH (c:TextChunk)
        WHERE toLower(c.text) CONTAINS toLower($query_text)
        RETURN c.text AS text
        """
        try:
            with self.driver.session() as session:
                results = session.run(query, {"query_text": query_text})
                return [record["text"] for record in results]
        except Exception as e:
            print(f"⚠️ Neo4j Text Query Error: {e}")
            return []

    def _generate_gemini_response(self, user_input: str, structured_data):
        """Generate chatbot response using Gemini LLM"""
        prompt = f"""
        You are an AI chatbot answering user queries based on structured knowledge.

        User's Query: {user_input}

        Knowledge Graph Data:
        {json.dumps(structured_data, indent=2)}

        Provide a user-friendly response explaining the answer in simple terms.
        """

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text if response else "⚠️ No response generated."
        except Exception as e:
            print(f"⚠️ Gemini API Error: {e}")
            return "⚠️ Error generating response from Gemini."
