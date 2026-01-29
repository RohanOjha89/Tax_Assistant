import sys
# ChromaDB/SQLite fix for AWS Fargate environments
if 'sqlite3' not in sys.modules or 'pysqlite3' in sys.modules:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from openai import OpenAI
import chromadb
from config import settings

class RAGPipeline:
        
    def __init__(self, collection, embedding_engine):
        # API_KEY is now pulled from settings (which pulls from AWS Secrets)
        self.client = OpenAI(api_key=settings.API_KEY)
        self.ee = embedding_engine
        self.collection = collection

    def retrieve(self, query: str, k: int = 3):
        # 1. Generate embedding for the search query
        query_vec = self.ee.generate([query])
        
        # 2. Query the collection (using standard list format for vectors)
        results = self.collection.query(query_embeddings=query_vec.tolist(), n_results=k)
    
        # 3. Join retrieved documents into a single context string
        context = " ".join(results['documents'][0])
        return context

    def generate_response(self, query, context, model_choice="SIMPLE"):
        model = settings.SIMPLE_MODEL if model_choice == "SIMPLE" else settings.COMPLEX_MODEL
        
        prompt = (
            f"You are a Tax Assistant. Answer the question strictly based on the provided context.\n\n"
            f"Context: {context}\n\n"
            f"Question: {query}\n\n"
            f"Answer:"
        )
        
        response = self.client.chat.completions.create(
            model=model, 
            messages=[{"role": "system", "content": "You are a professional tax advisor."}, {"role": "user", "content": prompt}])
        return response.choices[0].message.content