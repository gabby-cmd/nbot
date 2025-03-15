import streamlit as st
from neo4j import GraphDatabase
import json
import google.generativeai as genai
import time

class Chatbot:
    def __init__(self, uri, user, password, database="neo4j"):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        
        # Configure Gemini API
        try:
            GEMINI_API_KEY = st.secrets["gemini"]["api_key"]
            genai.configure(api_key=GEMINI_API_KEY)
            print("✅ Gemini API configured successfully")
        except Exception as e:
            print(f"❌ Error configuring Gemini API: {e}")

    def close(self):
        """Close Neo4j connection"""
        self.driver.close()

    def chat(self, user_input):
        """Process user query, retrieve knowledge from Neo4j, and generate chatbot response"""
        if not user_input or user_input.strip() == "":
            return "Please ask a question."
            
        # First try exact keyword search
        text_chunks = self._find_relevant_text_exact(user_input)
        
        # If no results, try fuzzy search with individual keywords
        if not text_chunks:
            print("🔍 No exact matches found, trying keyword search...")
            text_chunks = self._find_relevant_text_keywords(user_input)
            
        # If still no results, get some random chunks as context
        if not text_chunks:
            print("🔍 No keyword matches found, retrieving sample chunks...")
            text_chunks = self._get_sample_chunks()
        
        print(f"📚 Found {len(text_chunks)} relevant chunks")
        
        # Generate response using Gemini
        try:
            response = self._generate_gemini_response(user_input, text_chunks)
            return response
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return f"⚠️ Error generating response: {str(e)}"

    def _find_relevant_text_exact(self, query_text):
        """Retrieve relevant text chunks from Neo4j using exact match"""
        try:
            with self.driver.session() as session:
                results = session.run(
                    """
                    MATCH (c:TextChunk)
                    WHERE toLower(c.text) CONTAINS toLower($query_text)
                    RETURN c.text AS text
                    LIMIT 5
                    """,
                    query_text=query_text
                )
                return [record["text"] for record in results]
        except Exception as e:
            print(f"❌ Error querying Neo4j: {e}")
            return []

    def _find_relevant_text_keywords(self, query_text):
        """Retrieve relevant text chunks from Neo4j using keywords"""
        keywords = [word.strip().lower() for word in query_text.split() if len(word.strip()) > 3]
        results = []
        
        try:
            with self.driver.session() as session:
                for keyword in keywords:
                    query_results = session.run(
                        """
                        MATCH (c:TextChunk)
                        WHERE toLower(c.text) CONTAINS toLower($keyword)
                        RETURN c.text AS text
                        LIMIT 3
                        """,
                        keyword=keyword
                    )
                    for record in query_results:
                        if record["text"] not in results:
                            results.append(record["text"])
                            if len(results) >= 5:  # Limit to 5 chunks
                                return results
                return results
        except Exception as e:
            print(f"❌ Error querying Neo4j with keywords: {e}")
            return []

    def _get_sample_chunks(self, limit=3):
        """Get sample chunks from Neo4j when no relevant chunks are found"""
        try:
            with self.driver.session() as session:
                results = session.run(
                    """
                    MATCH (c:TextChunk)
                    RETURN c.text AS text
                    LIMIT $limit
                    """,
                    limit=limit
                )
                return [record["text"] for record in results]
        except Exception as e:
            print(f"❌ Error getting sample chunks: {e}")
            return []

    def _generate_gemini_response(self, user_input, text_chunks):
        """Generate chatbot response using Gemini AI"""
        if not text_chunks:
            return "I don't have enough information to answer that question. Please upload relevant documents."
            
        # Prepare context from chunks (limit total size)
        max_context_length = 10000
        context = ""
        for chunk in text_chunks:
            if len(context) + len(chunk) < max_context_length:
                context += chunk + "\n\n"
            else:
                break
                
        prompt = f"""
        You are a helpful assistant answering questions based on the provided document context.
        
        CONTEXT:
        {context}
        
        USER QUESTION: {user_input}
        
        Answer the user's question based ONLY on the information in the context provided.
        If the answer cannot be found in the context, say "I don't have enough information to answer that question."
        Be concise and accurate. Format your answer in a clear, readable way.
        """

        try:
            # Add retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    model = genai.GenerativeModel("gemini-pro")
                    response = model.generate_content(prompt)
                    
                    if response and hasattr(response, "text"):
                        return response.text
                    else:
                        print(f"⚠️ Empty response from Gemini (attempt {attempt+1})")
                        time.sleep(1)  # Wait before retry
                except Exception as e:
                    print(f"⚠️ Gemini API error (attempt {attempt+1}): {e}")
                    time.sleep(2)  # Wait before retry
                    
            return "⚠️ I encountered an issue generating a response. Please try again."
        except Exception as e:
            print(f"❌ Error with Gemini API: {e}")
            return f"⚠️ Error generating response: {str(e)}"

