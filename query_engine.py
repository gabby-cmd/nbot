import google.generativeai as genai
from neo4j import GraphDatabase
import json
import streamlit as st

# Load API Key
genai.configure(api_key=st.secrets["gemini"]["api_key"])

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
        entities = self._find_relevant_entities(user_input)
        text_chunks = self._find_relevant_text(user_input)

        structured_data = {
            "query": user_input,
            "entities": entities,
            "text_chunks": text_chunks
        }

        return self._generate_gemini_response(user_input, structured_data)

    def _find_relevant_entities(self, query_text: str):
        """Find relevant entities from Neo4j"""
        query = """
        MATCH (e:Entity)
        WHERE toLower(e.name) CONTAINS toLower($query)
        RETURN e.name AS name, e.type AS type
        """
        with self.driver.session() as session:
            results = session.run(query, query=query_text)
            return [{"name": record["name"], "type": record["type"]} for record in results]

    def _find_relevant_text(self, query_text: str):
        """Retrieve text chunks related to the query"""
        query = """
        MATCH (c:TextChunk)
        WHERE toLower(c.text) CONTAINS toLower($query)
        RETURN c.text AS text
        """
        with self.driver.session() as session:
            results = session.run(query, query=query_text)
            return [record["text"] for record in results]

    def _generate_gemini_response(self, user_input: str, structured_data):
        """Generate chatbot response using Gemini LLM with streaming"""
        prompt = f"""
        You are a chatbot that answers user queries based on structured knowledge.

        User's Query: {user_input}

        Knowledge Graph Data:
        {json.dumps(structured_data, indent=2)}

        Provide a conversational, user-friendly response explaining the answer in simple terms.
        """

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response_stream = model.generate_content_stream(prompt)

            for chunk in response_stream:
                if hasattr(chunk, "text"):  # ✅ Check if chunk has text
                    yield chunk.text
                else:
                    yield str(chunk)  # ✅ Convert any unexpected format to string
        except Exception as e:
            print(f"⚠️ Error generating Gemini response: {e}")
            yield "⚠️ Sorry, an error occurred while generating the response."
