import PyPDF2
from neo4j import GraphDatabase
import io

class DocumentProcessor:
    def __init__(self, uri, user, password):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def process_pdf(self, uploaded_file):
        """Extract text from a Streamlit uploaded PDF, chunk it, and store in Neo4j"""
        # Convert Streamlit's UploadedFile to a file-like object
        if hasattr(uploaded_file, "read"):
            file_obj = io.BytesIO(uploaded_file.read())
            text = self._extract_text_from_streamlit_pdf(file_obj)
        else:
            text = self._extract_text_from_pdf(uploaded_file)
            
        if not text:
            print("⚠️ No text extracted from the PDF!")
            return False

        chunks = self._chunk_text(text)
        if not chunks:
            print("⚠️ No chunks created from the text!")
            return False

        # Clear existing chunks before adding new ones
        self._clear_existing_chunks()

        # Store chunks in Neo4j
        success = self._store_chunks_in_neo4j(chunks)
        return success

    def _extract_text_from_streamlit_pdf(self, file_obj):
        """Extract text from a PDF file uploaded via Streamlit"""
        text = ""
        try:
            reader = PyPDF2.PdfReader(file_obj)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:  # Only add if text was extracted
                    text += page_text + "\n"
            
            print(f"📄 Extracted {len(reader.pages)} pages of text")
        except Exception as e:
            print(f"❌ Error extracting text from PDF: {e}")
        
        print(f"🔍 Extracted Text Length: {len(text)} chars")
        if text:
            print(f"🔍 Sample: {text[:200]}...")
        return text

    def _extract_text_from_pdf(self, file_path):
        """Extract text from a PDF file path"""
        text = ""
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"❌ Error extracting text from PDF: {e}")
        
        return text

    def _chunk_text(self, text, chunk_size=1000, overlap=200):
        """Split text into overlapping chunks"""
        chunks = []
        if not text:
            return chunks
            
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            if chunk.strip():  # Only add non-empty chunks
                chunks.append(chunk)
            start = end - overlap
        
        print(f"📌 Chunked into {len(chunks)} pieces of text")
        return chunks
        
    def _clear_existing_chunks(self):
        """Clear existing chunks from Neo4j"""
        try:
            with self.driver.session() as session:
                session.run("MATCH (c:TextChunk) DETACH DELETE c")
                print("🧹 Cleared existing chunks from Neo4j")
        except Exception as e:
            print(f"❌ Error clearing existing chunks: {e}")
    
    def _store_chunks_in_neo4j(self, chunks):
        """Store text chunks in Neo4j"""
        success = False
        try:
            with self.driver.session() as session:
                for i, chunk in enumerate(chunks):
                    session.run(
                        """
                        CREATE (c:TextChunk {id: $id, text: $text})
                        """,
                        id=f"chunk-{i}",
                        text=chunk
                    )
                print(f"✅ Successfully stored {len(chunks)} chunks in Neo4j")
                success = True
        except Exception as e:
            print(f"❌ Error storing chunks in Neo4j: {e}")
        
        return success

