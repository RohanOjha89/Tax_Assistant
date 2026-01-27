from sentence_transformers import SentenceTransformer
import faiss
import os
import numpy as np

class EmbeddingEngine:
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)

    def generate(self, texts):
        return self.model.encode(texts)
    
    def save_index(self, index, path):
        faiss.write_index(index, path)
        
    def load_index(self, path):
        if os.path.exists(path):
            return faiss.read_index(path)
        return None