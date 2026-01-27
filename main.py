import sys
# This makes ChromaDB use the newer pysqlite3 instead of the system sqlite3
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb
import os
import chromadb
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

# from config import DATA_PATH, EMBEDDING_MODEL_NAME
from config import settings
from src.document_processor import DocumentProcessor
from src.embedding_generation import EmbeddingEngine
from src.semantic_router import SemanticRouter
from src.rag_pipeline import RAGPipeline

# Global variables to hold our heavy objects
components = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown. This is where we initialize ChromaDB.
    """
    print("--- Initializing Systems ---")
    
    # 1. Initialize Embedding Engine
    ee = EmbeddingEngine(settings.EMBEDDING_MODEL_NAME)
    
    # 2. Get Path from Environment Variable (ECS setup)
    # Default to local path for testing, but use EFS path in production
    db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    print(f"--- Connecting to ChromaDB at: {db_path} ---")
    
    # 3. Initialize ChromaDB Persistent Client
    # Chroma stores data in the './chroma_db' folder by default
    chroma_client = chromadb.PersistentClient(path=db_path)
    collection = chroma_client.get_or_create_collection(name="tax_docs")
    
    # 4. Store in lifespan state
    components["router"] = SemanticRouter()
    components["rag"] = RAGPipeline(collection, ee) # Update RAGPipeline to accept Chroma collection
    components["ee"] = ee
    
    yield
    # Clean up on shutdown if necessary
    components.clear()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "online", "knowledge_base_size": components["rag"].collection.count()}

@app.post("/chat")
async def chat(query: str):
    try:
        router = components["router"]
        rag = components["rag"]
        
        # Strategy Decision
        classification = router.classify_query(query)
        
        # RAG Logic
        # Note: You'll need to update rag.retrieve to use collection.query()
        context = rag.retrieve(query)
        answer = rag.generate_response(query, context, classification)
        
        return {
            "query": query,
            "strategy": classification,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)