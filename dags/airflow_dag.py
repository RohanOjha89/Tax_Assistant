import sys
import os
# Add the directory containing config.py to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from airflow.decorators import dag, task

# Keep the SQLite patch at the top level to ensure the environment is ready
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

@dag(
    dag_id='tax_doc_ingestion_dag',
    schedule_interval=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['ingestion', 'chromadb']
)
def ingestion_dag():

    @task()
    def extract_from_s3(**kwargs):
        import boto3
        conf = kwargs.get('dag_run').conf or {}
        bucket = conf.get('bucket', 'your-default-bucket')
        key = conf.get('key', 'default-key.pdf')
        local_path = f"/tmp/{os.path.basename(key)}"
        
        s3 = boto3.client('s3')
        s3.download_file(bucket, key, local_path)
        return local_path

    @task()
    def chunk_documents(file_path: str):
        from src.document_processor import DocumentProcessor
        dp = DocumentProcessor(file_path)
        chunks = dp.load_and_chunk()
        return [c.page_content for c in chunks]

    @task()
    def generate_embeddings(texts: list):
        from src.embedding_generation import EmbeddingEngine
        from config import settings
        
        ee = EmbeddingEngine(settings.EMBEDDING_MODEL_NAME)
        embeddings = ee.generate(texts)
        return embeddings.tolist()

    @task()
    def update_chroma_db(embeddings: list, texts: list):
        import chromadb
        from config import settings
        
        # Use the settings object consistently
        client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        collection = client.get_or_create_collection(name=settings.COLLECTION_NAME)
        
        ids = [f"id_{i}_{datetime.now().timestamp()}" for i in range(len(texts))]
        collection.add(embeddings=embeddings, documents=texts, ids=ids)
        return "Success"

    # Execution Sequence
    path = extract_from_s3()
    chunks = chunk_documents(path)
    vectors = generate_embeddings(chunks)
    update_chroma_db(vectors, chunks)

ingestion_dag()