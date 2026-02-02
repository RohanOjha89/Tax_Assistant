import sys
# 1. THE ABSOLUTE FIRST STEP: SQLite Patch
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass 

# 2. LOAD CONFIG FIRST: This forces Pydantic to validate the environment early
from config import settings 

# 3. NOW IMPORT HEAVY LIBS: Chroma, FastAPI, etc.
import chromadb
import os
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

<<<<<<< HEAD
# from config import DATA_PATH, EMBEDDING_MODEL_NAME
from config import settings
=======
# 4. CUSTOM MODULES LAST: They depend on everything above
>>>>>>> df1c26c (Modified all the files)
from src.document_processor import DocumentProcessor
from src.embedding_generation import EmbeddingEngine
from src.semantic_router import SemanticRouter
from src.rag_pipeline import RAGPipeline

components = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- Initializing Systems ---")
    
<<<<<<< HEAD
    ee = EmbeddingEngine(settings.EMBEDDING_MODEL_NAME)
    
    # Use the path and collection name from settings to stay consistent
    chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
    collection = chroma_client.get_or_create_collection(name=settings.COLLECTION_NAME)
    
    components["router"] = SemanticRouter()
    # This now matches the updated RAGPipeline __init__
    components["rag"] = RAGPipeline(collection, ee) 
=======
    # Use settings from config.py
    ee = EmbeddingEngine(settings.EMBEDDING_MODEL_NAME)
    
    # Ensure we use the path from our settings object
    db_path = settings.CHROMA_PATH
    print(f"--- Connecting to ChromaDB at: {db_path} ---")
    
    chroma_client = chromadb.PersistentClient(path=db_path)
    collection = chroma_client.get_or_create_collection(name=settings.COLLECTION_NAME)
    
    components["router"] = SemanticRouter()
    components["rag"] = RAGPipeline(collection, ee)
>>>>>>> df1c26c (Modified all the files)
    components["ee"] = ee
    yield
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