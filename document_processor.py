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
        if not text:
            print("⚠️ No text extracted from the PDF!")
            return

        chunks = self._chunk_text(text)
        if not chunks:
            print("⚠️ No chunks created from the text!")
            return

        with self.driver.session() as session:
            for i, chunk in enumerate(chunks):
                try:
                    session.run(
                        """
                        CREATE (c:TextChunk {id: $id, text: $text})
                        """,
                        id=f"chunk-{i}",
                        text=chunk
                    )
                    print(f"✅ Stored chunk-{i} in Neo4j")
                except Exception as e:
                    print(f"❌ Error storing chunk-{i}: {e}")

    def _extract_text_from_pdf(self, file_path):
        """Extract text from a PDF file"""
        text = ""
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"❌ Error extracting text from PDF: {e}")
        
        print(f"🔍 Extracted Text (First 500 chars): {text[:500]}")
        return text

    def _chunk_text(self, text, chunk_size=1000, overlap=200):
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        print(f"📌 Chunked into {len(chunks)} pieces of text")
        return chunks
