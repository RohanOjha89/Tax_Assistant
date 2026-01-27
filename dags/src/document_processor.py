### FROM GEMINI
# from langchain.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_and_chunk(self):
        loader = PyPDFLoader(self.file_path)
        documents = loader.load()
        
        # Use recursive splitter for better legal context preservation
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        return text_splitter.split_documents(documents)




### FROM DEEPSEEK
# from pathlib import Path
# from typing import List, Dict, Any
# import json
# from dataclasses import dataclass
# from pypdf import PdfReader
# import hashlib
# from config import Config

# @dataclass
# class DocumentChunk:
#     """Data class for document chunks"""
#     id: str
#     text: str
#     page_number: int
#     chunk_index: int
#     metadata: Dict[str, Any]

# class DocumentProcessor:
#     """Handles PDF loading, chunking, and storage"""
    
#     def __init__(self, config: Config = Config):
#         self.config = config
#         self.chunks: List[DocumentChunk] = []
        
#     def load_pdf(self, pdf_path: Path = None) -> str:
#         """Load and extract text from PDF"""
#         if pdf_path is None:
#             pdf_path = self.config.PDF_PATH
            
#         print(f"Loading PDF: {pdf_path}")
#         reader = PdfReader(pdf_path)
#         full_text = ""
        
#         for page_num, page in enumerate(reader.pages):
#             text = page.extract_text()
#             full_text += f"\n\n--- Page {page_num + 1} ---\n{text}"
            
#         return full_text
    
#     def chunk_text(self, text: str) -> List[DocumentChunk]:
#         """Split text into overlapping chunks"""
#         from nltk.tokenize import sent_tokenize, word_tokenize
#         import nltk
        
#         # Download NLTK data if not present
#         try:
#             nltk.data.find('tokenizers/punkt')
#         except LookupError:
#             nltk.download('punkt')
        
#         sentences = sent_tokenize(text)
#         chunks = []
#         current_chunk = []
#         current_word_count = 0
#         chunk_index = 0
        
#         for sentence in sentences:
#             sentence_words = word_tokenize(sentence)
#             sentence_word_count = len(sentence_words)
            
#             # If adding this sentence exceeds chunk size, save current chunk
#             if current_word_count + sentence_word_count > self.config.CHUNK_SIZE and current_chunk:
#                 chunk_text = ' '.join(current_chunk)
#                 chunk_id = hashlib.md5(chunk_text.encode()).hexdigest()[:16]
                
#                 chunks.append(DocumentChunk(
#                     id=chunk_id,
#                     text=chunk_text,
#                     page_number=self._extract_page_number(chunk_text),
#                     chunk_index=chunk_index,
#                     metadata={
#                         "source": "Income Tax Act, 1961",
#                         "chunk_size_words": current_word_count
#                     }
#                 ))
#                 chunk_index += 1
                
#                 # Keep overlap for next chunk
#                 overlap_words = []
#                 overlap_count = 0
#                 for sent in reversed(current_chunk):
#                     sent_words = word_tokenize(sent)
#                     if overlap_count + len(sent_words) <= self.config.CHUNK_OVERLAP:
#                         overlap_words.insert(0, sent)
#                         overlap_count += len(sent_words)
#                     else:
#                         break
                
#                 current_chunk = overlap_words
#                 current_word_count = overlap_count
            
#             current_chunk.append(sentence)
#             current_word_count += sentence_word_count
        
#         # Add the last chunk
#         if current_chunk:
#             chunk_text = ' '.join(current_chunk)
#             chunk_id = hashlib.md5(chunk_text.encode()).hexdigest()[:16]
            
#             chunks.append(DocumentChunk(
#                 id=chunk_id,
#                 text=chunk_text,
#                 page_number=self._extract_page_number(chunk_text),
#                 chunk_index=chunk_index,
#                 metadata={
#                     "source": "Income Tax Act, 1961",
#                     "chunk_size_words": current_word_count
#                 }
#             ))
        
#         self.chunks = chunks
#         print(f"Created {len(chunks)} chunks from document")
#         return chunks
    
#     def _extract_page_number(self, text: str) -> int:
#         """Extract page number from chunk text"""
#         import re
#         match = re.search(r'--- Page (\d+) ---', text)
#         return int(match.group(1)) if match else 0
    
#     def save_chunks(self, output_path: Path = None):
#         """Save chunks to JSON for debugging/reuse"""
#         if output_path is None:
#             output_path = self.config.PROCESSED_DIR / "chunks.json"
        
#         chunks_data = [
#             {
#                 "id": chunk.id,
#                 "text": chunk.text,
#                 "page_number": chunk.page_number,
#                 "chunk_index": chunk.chunk_index,
#                 "metadata": chunk.metadata
#             }
#             for chunk in self.chunks
#         ]
        
#         with open(output_path, 'w', encoding='utf-8') as f:
#             json.dump(chunks_data, f, indent=2, ensure_ascii=False)
        
#         print(f"Saved {len(chunks_data)} chunks to {output_path}")
    
#     def load_chunks(self, input_path: Path = None) -> List[DocumentChunk]:
#         """Load chunks from JSON file"""
#         if input_path is None:
#             input_path = self.config.PROCESSED_DIR / "chunks.json"
        
#         with open(input_path, 'r', encoding='utf-8') as f:
#             chunks_data = json.load(f)
        
#         self.chunks = [
#             DocumentChunk(
#                 id=chunk["id"],
#                 text=chunk["text"],
#                 page_number=chunk["page_number"],
#                 chunk_index=chunk["chunk_index"],
#                 metadata=chunk["metadata"]
#             )
#             for chunk in chunks_data
#         ]
        
#         print(f"Loaded {len(self.chunks)} chunks from {input_path}")
#         return self.chunks
    
#     def process_document(self, pdf_path: Path = None) -> List[DocumentChunk]:
#         """Complete document processing pipeline"""
#         text = self.load_pdf(pdf_path)
#         chunks = self.chunk_text(text)
#         self.save_chunks()
#         return chunks