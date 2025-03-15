import google.generativeai as genai
from neo4j import GraphDatabase
import json
import streamlit as st

# ✅ Configure Gemini API
genai.configure(api_key=st.secrets["gemini"]["api_key"])

class Chatbot:
    def __init__(self):
        """Initialize Neo4j connection"""
        self.uri = st.secrets["neo4j"]["uri"]
        self.user = st.secrets["neo4j"]["user"]
        self.password = st.secrets["neo4j"]["password"]
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

        # ✅ Verify Connection
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")  # Simple test query
            print("✅ Connected to Neo4j successfully!")
        except Exception as e:
            print(f"🚨 Failed to connect to Neo4j: {e}")

    def close(self):
        """Close Neo4j connection"""
        self.driver.close()

    def chat(self, user_input: str):
        """Process user query, retrieve knowledge from Neo4j, and generate chatbot response"""
        try:
            entities = self._find_relevant_entities(user_input)
            relationships = self._find_relevant_relationships(user_input)

            structured_data = {
                "query": user_input,
                "entities": entities,
                "relationships": relationships
            }

            return self._generate_gemini_response(user_input, structured_data)

        except Exception as e:
            print(f"🚨 Error in chatbot processing: {e}")
            return [f"🚨 Error: {str(e)}"]  # Return an error message for debugging

    def _find_relevant_entities(self, query_text: str):
        """Find relevant entities from Neo4j"""
        query = """
        MATCH (e:Entity)
        WHERE toLower(e.name) CONTAINS toLower($query)
        RETURN e.name AS name, e.type AS type
        """
        with self.driver.session() as session:
            try:
                results = session.run(query, query=query_text)
                return [{"name": record["name"], "type": record["type"]} for record in results]
            except Exception as e:
                print(f"🚨 Neo4j query error (entities): {e}")
                return []

    def _find_relevant_relationships(self, query_text: str):
        """Find relationships in Neo4j"""
        query = """
        MATCH (a:Entity)-[r]->(b:Entity)
        WHERE toLower(a.name) CONTAINS toLower($query) OR toLower(b.name) CONTAINS toLower($query)
        RETURN a.name AS source, type(r) AS relationship, b.name AS target
        """
        with self.driver.session() as session:
            try:
                results = session.run(query, query=query_text)
                return [{"source": record["source"], "relationship": record["relationship"], "target": record["target"]} for record in results]
            except Exception as e:
                print(f"🚨 Neo4j query error (relationships): {e}")
                return []

    def _generate_gemini_response(self, user_input: str, structured_data):
        """Generate chatbot response using Gemini LLM with streaming"""
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
