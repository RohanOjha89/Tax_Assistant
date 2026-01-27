from openai import OpenAI
from config import API_KEY, SIMPLE_MODEL, COMPLEX_MODEL
from dotenv import load_dotenv

class RAGPipeline:
    def __init__(self, index, chunks, embedding_engine):
        self.client = OpenAI(api_key=API_KEY)
        self.index = index
        self.chunks = chunks
        self.embedding_engine = embedding_engine

    def retrieve(self, query: str, k: int = 3):
        # Generate embedding for the query
        query_vec = self.ee.generate([query]).tolist()
    
        # Chroma query
        results = self.collection.query(query_embeddings=query_vec, n_results=k)
    
        # Chroma returns a nested list of documents
        return " ".join(results['documents'][0])

    def generate_response(self, query, context, model_choice):
        model = SIMPLE_MODEL if model_choice == "SIMPLE" else COMPLEX_MODEL
        prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer strictly based on context:"
        
        response = self.client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content