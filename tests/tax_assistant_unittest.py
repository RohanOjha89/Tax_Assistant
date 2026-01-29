import sys
from unittest.mock import patch, MagicMock
import unittest
import numpy as np

# Mock sqlite3 for ChromaDB compatibility
if 'sqlite3' not in sys.modules or 'pysqlite3' in sys.modules:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from src.semantic_router import SemanticRouter
from src.embedding_generation import EmbeddingEngine
from config import settings  # Import the settings object

class TestTaxAssistantLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize Engine with the model name from the settings object
        cls.ee = EmbeddingEngine(settings.EMBEDDING_MODEL_NAME)
        cls.router = SemanticRouter()

    @patch("openai.resources.chat.completions.Completions.create")
    def test_semantic_router_simple_query(self, mock_openai):
        """Test if a basic factual query is classified as SIMPLE"""
        # Mocking the OpenAI response object structure
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="SIMPLE"))]
        mock_openai.return_value = mock_response

        query = "What is Section 80C?"
        classification = self.router.classify_query(query)
        self.assertEqual(classification, "SIMPLE")

    @patch("openai.resources.chat.completions.Completions.create")
    def test_semantic_router_complex_query(self, mock_openai):
        """Test if a calculation query is classified as COMPLEX"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="COMPLEX"))]
        mock_openai.return_value = mock_response

        query = "Calculate my tax for 15L income"
        classification = self.router.classify_query(query)
        self.assertEqual(classification, "COMPLEX")

    def test_embedding_dimensions(self):
        """Ensure the embedding engine returns the correct vector size (384 for MiniLM)"""
        sample_text = ["test document"]
        embedding = self.ee.generate(sample_text)
        
        # Check dimensions: all-MiniLM-L6-v2 is 384
        self.assertEqual(embedding.shape[1], 384)
        self.assertIsInstance(embedding, np.ndarray)

if __name__ == "__main__":
    unittest.main()