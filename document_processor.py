import PyPDF2
from neo4j import GraphDatabase
import io
import streamlit as st

class DocumentProcessor:
    def __init__(self, uri, user, password):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def process_pdf(self, uploaded_file):
        """Extract text from a Streamlit uploaded PDF, chunk it, and store in Neo4j"""
        try:
            # Verify the uploaded file
            if uploaded_file is None:
                st.error("No file was uploaded")
                return False
                
            # Debug information
            st.info(f"Processing file: {uploaded_file.name}, Size: {uploaded_file.size} bytes")
            
            # Extract text from the PDF
            text = self._extract_text_from_streamlit_file(uploaded_file)
            
            if not text or len(text.strip()) == 0:
                st.warning("⚠️ No text could be extracted from the PDF!")
                return False

            st.info(f"Extracted {len(text)} characters of text")
                
            # Chunk the text
            chunks = self._chunk_text(text)
            if not chunks or len(chunks) == 0:
                st.warning("⚠️ No chunks created from the text!")
                return False
                
            st.info(f"Created {len(chunks)} text chunks")

            # Clear existing chunks before adding new ones
            self._clear_existing_chunks()

            # Store chunks in Neo4j
            success = self._store_chunks_in_neo4j(chunks)
            return success
            
        except Exception as e:
            st.error(f"Error processing document: {str(e)}")
            return False

    def _extract_text_from_streamlit_file(self, uploaded_file):
        """Extract text from a PDF file uploaded via Streamlit"""
        text = ""
        try:
            # Read the file content
            bytes_data = uploaded_file.getvalue()
            
            # Create a file-like object
            file_stream = io.BytesIO(bytes_data)
            
            # Use PyPDF2 to extract text
            try:
                reader = PyPDF2.PdfReader(file_stream)
                
                # Debug info
                st.info(f"PDF has {len(reader.pages)} pages")
                
                # Extract text from each page
                for i, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as e:
                        st.warning(f"Error extracting text from page {i+1}: {str(e)}")
                
            except Exception as e:
                st.error(f"Error reading PDF: {str(e)}")
                return ""
                
        except Exception as e:
            st.error(f"Error processing uploaded file: {str(e)}")
            return ""
        
        return text

    def _chunk_text(self, text, chunk_size=1000, overlap=200):
        """Split text into overlapping chunks"""
        chunks = []
        if not text or len(text.strip()) == 0:
            return chunks
            
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            if chunk.strip():  # Only add non-empty chunks
                chunks.append(chunk)
            start = end - overlap
            
            # Safety check to prevent infinite loops
            if end == len(text) or start >= end:
                break
        
        return chunks
        
    def _clear_existing_chunks(self):
        """Clear existing chunks from Neo4j"""
        try:
            with self.driver.session() as session:
                session.run("MATCH (c:TextChunk) DETACH DELETE c")
                st.info("🧹 Cleared existing chunks from Neo4j")
                return True
        except Exception as e:
            st.error(f"Error clearing existing chunks: {str(e)}")
            return False
    
    def _store_chunks_in_neo4j(self, chunks):
        """Store text chunks in Neo4j"""
        success = False
        try:
            with self.driver.session() as session:
                # Create a transaction function to batch the inserts
                def create_chunks_tx(tx, chunk_batch):
                    for i, chunk in enumerate(chunk_batch):
                        tx.run(
                            """
                            CREATE (c:TextChunk {id: $id, text: $text})
                            """,
                            id=f"chunk-{i}",
                            text=chunk
                        )
                
                # Process in smaller batches to avoid transaction timeouts
                batch_size = 10
                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i:i+batch_size]
                    session.execute_write(create_chunks_tx, batch)
                    st.info(f"Stored batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")
                
                st.success(f"✅ Successfully stored {len(chunks)} chunks in Neo4j")
                success = True
        except Exception as e:
            st.error(f"Error storing chunks in Neo4j: {str(e)}")
            success = False
        
        return success


         
