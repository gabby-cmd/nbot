import streamlit as st
from neo4j import GraphDatabase
import json
import google.generativeai as genai

# ✅ Load API Key from Streamlit secrets
GEMINI_API_KEY = st.secrets["gemini"]["api_key"]
genai.configure(api_key=GEMINI_API_KEY)

class Chatbot:
    def __init__(self, uri, user, password, database="neo4j"):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        """Close Neo4j connection"""
        self.driver.close()

    def chat(self, user_input):
        """Process user query, retrieve knowledge from Neo4j, and generate chatbot response"""
        text_chunks = self._find_relevant_text(user_input)

        structured_data = {
            "query": user_input,
            "text_chunks": text_chunks
        }

        return self._generate_gemini_response(user_input, structured_data)

    def _find_relevant_text(self, query_text):
        """Retrieve relevant text chunks from Neo4j"""
        query = """
        MATCH (c:TextChunk)
        WHERE toLower(c.text) CONTAINS toLower($query_text)
        RETURN c.text AS text
        """
        with self.driver.session() as session:
            results = session.run(query, query_text=query_text)
            return [record["text"] for record in results]

    def _generate_gemini_response(self, user_input, structured_data):
        """Generate chatbot response using Gemini AI"""
        prompt = f"""
        You are a chatbot answering user queries based on stored document text.

        User's Query: {user_input}

        Extracted Text from Neo4j:
        {json.dumps(structured_data, indent=2)}

        Provide a clear, informative response based on the extracted data.
        """

        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        
        return response.text if response else "⚠️ No relevant information found."

# ✅ Close Neo4j connection on exit
if __name__ == "__main__":
    chatbot = Chatbot(uri="neo4j+s://your-instance.databases.neo4j.io", user="neo4j", password="your-password")
    print(chatbot.chat("What is the refund policy?"))
    chatbot.close()
