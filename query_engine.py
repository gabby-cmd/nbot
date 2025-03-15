import google.generativeai as genai
from neo4j import GraphDatabase
import streamlit as st  # Import Streamlit for Secrets

# Load API keys from Streamlit Secrets
genai.configure(api_key=st.secrets["gemini"]["api_key"])

# Load Neo4j credentials from Streamlit Secrets
URI = st.secrets["neo4j"]["uri"]
AUTH = (st.secrets["neo4j"]["user"], st.secrets["neo4j"]["password"])

# Verify Neo4j Connection
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connected to Neo4j successfully!")

class Chatbot:
    def __init__(self):
        """Initialize Neo4j connection"""
        self.uri = URI
        self.user = AUTH[0]
        self.password = AUTH[1]
        self.database = "neo4j"

        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def chat(self, user_input: str):
        """Retrieve knowledge from Neo4j and generate chatbot response"""
        entities = self._find_relevant_entities(user_input)
        relationships = self._find_relevant_relationships(user_input)

        structured_data = {
            "query": user_input,
            "entities": entities,
            "relationships": relationships
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

    def _find_relevant_relationships(self, query_text: str):
        """Find relationships in Neo4j"""
        query = """
        MATCH (a:Entity)-[r]->(b:Entity)
        WHERE toLower(a.name) CONTAINS toLower($query) OR toLower(b.name) CONTAINS toLower($query)
        RETURN a.name AS source, type(r) AS relationship, b.name AS target
        """
        with self.driver.session() as session:
            results = session.run(query, query=query_text)
            return [{"source": record["source"], "relationship": record["relationship"], "target": record["target"]} for record in results]

    def _generate_gemini_response(self, user_input: str, structured_data):
        """Generate chatbot response using Gemini 1.5 Flash"""
        prompt = f"""
        You are a chatbot that answers user queries based on structured knowledge.

        User's Query: {user_input}

        Knowledge Graph Data:
        {json.dumps(structured_data, indent=2)}

        Provide a conversational, user-friendly response.
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response_stream = model.generate_content_stream(prompt)

        return response_stream  #  Streams response in real-time
