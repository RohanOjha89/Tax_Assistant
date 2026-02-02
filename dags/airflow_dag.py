import numpy as np
print(f"DEBUG: Current NumPy version is {np.__version__}")

import sys
# MUST be at the very top for ChromaDB compatibility in Fargate
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import boto3
from airflow.decorators import dag, task
from datetime import datetime
import os
import chromadb
from src.document_processor import DocumentProcessor
from src.embedding_generation import EmbeddingEngine
# config.py should point CHROMA_PATH to "/opt/airflow/chroma_db"
# from config import CHROMA_PATH, COLLECTION_NAME
from config import settings

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
        # ... (Your current code is good, but use /tmp for truly transient files)
        conf = kwargs.get('dag_run').conf
        bucket = conf.get('bucket')
        key = conf.get('key')
        local_path = f"/tmp/{os.path.basename(key)}"
        
        # Tip: Use boto3 here to download the file
        s3 = boto3.client('s3')
        s3.download_file(bucket, key, local_path)
        return local_path

    @task()
    def chunk_documents(file_path: str):
        dp = DocumentProcessor(file_path)
        chunks = dp.load_and_chunk()
        return [c.page_content for c in chunks] # Return serializable data

    @task()
    def generate_embeddings(texts: list):
        ee = EmbeddingEngine()
        embeddings = ee.generate(texts)
        return embeddings.tolist()

    @task()
    def update_chroma_db(embeddings: list, texts: list):
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = client.get_or_create_collection(name=COLLECTION_NAME)
        ids = [f"id_{i}_{datetime.now().timestamp()}" for i in range(len(texts))]
        collection.add(embeddings=embeddings, documents=texts, ids=ids)
        return "Success"

    # Define execution sequence
    file_path = extract_from_s3()
    chunks = chunk_documents(file_path)
    vectors = generate_embeddings(chunks)
    update_chroma_db(vectors, chunks)

ingestion_dag()