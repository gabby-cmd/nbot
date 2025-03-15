import re
import os
import PyPDF2
from neo4j import GraphDatabase

class DocumentProcessor:
    def __init__(self, uri, user, password):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def process_pdf(self, file_path):
        """Extract text from a PDF, chunk it, and store in Neo4j"""
        text = self._extract_text_from_pdf(file_path)
        chunks = self._chunk_text(text)

        with self.driver.session() as session:
            for i, chunk in enumerate(chunks):
                session.run("""
                CREATE (c:TextChunk {id: $id, text: $text})
                """, id=f"chunk-{i}", text=chunk)

    def _extract_text_from_pdf(self, file_path):
        """Extract text from a PDF file"""
        text = ""
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"🚨 Error reading PDF: {e}")
        return text

    def _chunk_text(self, text, chunk_size=1000, overlap=200):
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
        return chunks

#  Example Usage
if __name__ == "__main__":
    processor = DocumentProcessor("neo4j+s://your-aura-instance.databases.neo4j.io", "neo4j", "your-password")
    processor.process_pdf("your_file.pdf")
