import sys
# ChromaDB/SQLite fix for AWS Fargate environments
if 'sqlite3' not in sys.modules or 'pysqlite3' in sys.modules:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from openai import OpenAI
import chromadb
from config import settings

class RAGPipeline:
    def __init__(self, embedding_engine):
        # API_KEY is now pulled from settings (which pulls from AWS Secrets)
        self.client = OpenAI(api_key=settings.API_KEY)
        self.ee = embedding_engine
        
        # Initialize Chroma Client pointing to our EFS path
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        self.collection = self.chroma_client.get_or_create_collection(name=settings.COLLECTION_NAME)

    def retrieve(self, query: str, k: int = 3):
        """
        Retrieves the most relevant chunks from the persistent ChromaDB.
        """
        # 1. Generate embedding for the search query
        query_vec = self.ee.generate([query])
        
        # 2. Query the collection (using standard list format for vectors)
        results = self.collection.query(
            query_embeddings=query_vec.tolist(), 
            n_results=k
        )
    
        # 3. Join retrieved documents into a single context string
        # Chroma returns a list of lists, so we take the first element [0]
        context = " ".join(results['documents'][0])
        return context

    def generate_response(self, query, context, model_choice="SIMPLE"):
        """
        Uses OpenAI to generate a grounded answer based on the retrieved context.
        """
        # Select model from centralized settings
        model = settings.SIMPLE_MODEL if model_choice == "SIMPLE" else settings.COMPLEX_MODEL
        
        prompt = (
            f"You are a Tax Assistant. Answer the question strictly based on the provided context.\n\n"
            f"Context: {context}\n\n"
            f"Question: {query}\n\n"
            f"Answer:"
        )
        
        response = self.client.chat.completions.create(
            model=model, 
            messages=[{"role": "system", "content": "You are a professional tax advisor."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content