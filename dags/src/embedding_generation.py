import sys
# ChromaDB/SQLite fix for AWS Fargate environments
if 'sqlite3' not in sys.modules or 'pysqlite3' in sys.modules:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from sentence_transformers import SentenceTransformer
import numpy as np
from config import settings

class EmbeddingEngine:
    def __init__(self, model_name=None):
        # Use the model name from config if none provided
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        print(f"--- Loading Embedding Model: {self.model_name} ---")
        self.model = SentenceTransformer(self.model_name)

    def generate(self, texts):
        """
        Generates embeddings for a list of strings.
        Returns a numpy array or list of floats.
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(texts)
        return embeddings