import sys
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import unittest
import numpy as np
from src.semantic_router import SemanticRouter
from src.embedding_generation import EmbeddingEngine
from config import EMBEDDING_MODEL_NAME

class TestTaxAssistantLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize once for all tests in this class
        cls.router = SemanticRouter()
        cls.ee = EmbeddingEngine(EMBEDDING_MODEL_NAME)

    def test_semantic_router_tax_query(self):
        # Test if a tax-related query is correctly classified
        query = "How do I save tax under 80C?"
        classification = self.router.classify_query(query)
        self.assertEqual(classification, "tax_query")

    def test_semantic_router_greeting(self):
        # Test non-tax query classification
        query = "Hello, how are you?"
        classification = self.router.classify_query(query)
        self.assertEqual(classification, "greeting")

    def test_embedding_dimensions(self):
        # Ensure the embedding engine returns the correct vector size
        sample_text = ["test document"]
        embedding = self.ee.generate(sample_text)
        # Assuming your model (like all-MiniLM-L6-v2) is 384 dimensions
        self.assertEqual(embedding.shape[1], 384)
        self.assertIsInstance(embedding, np.ndarray)

if __name__ == "__main__":
    unittest.main()