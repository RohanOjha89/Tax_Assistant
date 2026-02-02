import sys
<<<<<<< HEAD
# This must happen BEFORE importing chromadb
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

=======
>>>>>>> df1c26c (Modified all the files)
import os
import json

# --- 1. THE MANDATORY PATCH (Must be before chromadb/pydantic) ---
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    # If pysqlite3-binary isn't installed, we fall back to system sqlite
    pass

import boto3
from botocore.exceptions import ClientError
from pydantic_settings import BaseSettings

def get_aws_secret(secret_name, region_name="us-east-1"):
    """Fetches secrets from AWS Secrets Manager"""
<<<<<<< HEAD
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
=======
>>>>>>> df1c26c (Modified all the files)
    try:
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager', region_name=region_name)
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except Exception as e:
        print(f"AWS Secret fallback: {e}")
        return {}

class Settings(BaseSettings):
    # --- Secrets/Env Vars ---
<<<<<<< HEAD
    API_KEY: str = os.getenv("API_KEY", "") 
=======
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
>>>>>>> df1c26c (Modified all the files)
    ROUTER_MODEL: str = os.getenv("ROUTER_MODEL", "gpt-4.1-nano")
    SIMPLE_MODEL: str = os.getenv("SIMPLE_MODEL", "gpt-4.1-nano")
    COMPLEX_MODEL: str = os.getenv("COMPLEX_MODEL", "gpt-4.1-mini")
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # --- Paths & Persistence ---
    CHROMA_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    # Adding DATA_PATH back for main.py compatibility
    DATA_PATH: str = os.getenv("DATA_PATH", "./data") 
    COLLECTION_NAME: str = "tax_docs"

    def __init__(self, **values):
        super().__init__(**values)
<<<<<<< HEAD
        # Only load from AWS if explicitly in prod and API_KEY is missing
        if os.getenv("ENV") == "prod" and not self.API_KEY:
=======
        if os.getenv("ENV") == "prod" and not self.OPENAI_API_KEY:
>>>>>>> df1c26c (Modified all the files)
            aws_secrets = get_aws_secret("prod/tax_assistant/config")
            if "API_KEY" in aws_secrets:
                self.API_KEY = aws_secrets["API_KEY"]
            # Map other potential keys from AWS
            for key in ["ROUTER_MODEL", "SIMPLE_MODEL", "COMPLEX_MODEL"]:
                if key in aws_secrets:
                    setattr(self, key, aws_secrets[key])

<<<<<<< HEAD
# IMPORTANT: This line MUST exist at the bottom for 'from config import settings' to work
settings = Settings()
=======
# Create a single instance
settings = Settings()

# --- 4. EXPLICIT EXPORTS (Fixes "ImportError: cannot import name X from config") ---
CHROMA_PATH = settings.CHROMA_PATH
COLLECTION_NAME = settings.COLLECTION_NAME
DATA_PATH = settings.DATA_PATH
EMBEDDING_MODEL_NAME = settings.EMBEDDING_MODEL_NAME
>>>>>>> df1c26c (Modified all the files)
