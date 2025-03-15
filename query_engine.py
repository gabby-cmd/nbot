from neo4j import GraphDatabase
import google.generativeai as genai
import json

# ✅ Configure Gemini LLM API Key
genai.configure(api_key="your-gemini-api-key")

class Chatbot:
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        """✅ Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        """✅ Close Neo4j connection"""
        self.driver.close()

    def chat(self, user_input: str):
        """✅ Process user query, retrieve knowledge from Neo4j, and generate chatbot response"""
        entities = self._find_relevant_entities(user_input)
        relationships = self._find_relevant_relationships(user_input)

        structured_data = {
            "query": user_input,
            "entities": entities,
            "relationships": relationships
        }

        return self._generate_gemini_response(user_input, structured_data)

    def _find_relevant_entities(self, query_text: str):
        """✅ Find relevant entities from Neo4j"""
        query = """
        MATCH (e:TextChunk)
        WHERE toLower(e.text) CONTAINS toLower($query)
        RETURN e.text AS text
        """
        with self.driver.session() as session:
            results = session.run(query, query=query_text)
            return [{"text": record["text"]} for record in results]

    def _find_relevant_relationships(self, query_text: str):
        """✅ Find relationships in Neo4j"""
        query = """
        MATCH (a:TextChunk)-[r]->(b:TextChunk)
        WHERE toLower(a.text) CONTAINS toLower($query) OR toLower(b.text) CONTAINS toLower($query)
        RETURN a.text AS source, type(r) AS relationship, b.text AS target
        """
        with self.driver.session() as session:
            results = session.run(query, query=query_text)
            return [{"source": record["source"], "relationship": record["relationship"], "target": record["target"]} for record in results]

    def _generate_gemini_response(self, user_input: str, structured_data):
        """✅ Generate chatbot response using Gemini LLM"""
        prompt = f"""
        You are a chatbot that answers user queries based on structured knowledge.

        User's Query: {user_input}

        Knowledge Graph Data:
        {json.dumps(structured_data, indent=2)}

        Provide a conversational, user-friendly response explaining the answer in simple terms.
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response_stream = model.generate_content_stream(prompt)

        return response_stream  # ✅ Returns a streaming generator
