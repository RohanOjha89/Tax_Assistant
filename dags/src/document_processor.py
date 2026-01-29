from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

class DocumentProcessor:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_and_chunk(self):
        # 1. Load the PDF
        loader = PyPDFLoader(self.file_path)
        documents = loader.load()
        
        # 2. Add extra metadata (e.g., filename) to every page
        # This helps the LLM cite its sources correctly later
        filename = os.path.basename(self.file_path)
        for doc in documents:
            doc.metadata["source_file"] = filename
        
        # 3. Use recursive splitter (Industry standard for legal context)
        # chunk_overlap ensures context isn't lost at the boundaries
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=150,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"--- Processed {filename}: Created {len(chunks)} chunks ---")
        return chunks