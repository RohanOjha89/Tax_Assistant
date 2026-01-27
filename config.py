import os
import json
import boto3
from botocore.exceptions import ClientError
from pydantic_settings import BaseSettings

def get_aws_secret(secret_name, region_name="us-east-1"):
    """Fetches secrets from AWS Secrets Manager"""
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except ClientError as e:
        # Fallback for local development if secret isn't found
        print(f"AWS Secret not found, falling back to local environment: {e}")
        return {}

class Settings(BaseSettings):
    # --- Secrets/Env Vars ---
    # These will pull from ECS Environment Variables first
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ROUTER_MODEL: str = os.getenv("ROUTER_MODEL", "gpt-4.1-nano")
    SIMPLE_MODEL: str = os.getenv("SIMPLE_MODEL", "gpt-4.1-nano")
    COMPLEX_MODEL: str = os.getenv("COMPLEX_MODEL", "gpt-4.1-mini")
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # --- Paths & Persistence ---
    # Use the CHROMA_DB_PATH we set in ECS, fallback to local for your laptop
    CHROMA_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    COLLECTION_NAME: str = "tax_docs"

    def __init__(self, **values):
        super().__init__(**values)
        # Load secrets only if explicitely in prod and env vars are missing
        if os.getenv("ENV") == "prod" and not self.OPENAI_API_KEY:
            aws_secrets = get_aws_secret("prod/tax_assistant/config")
            for key, value in aws_secrets.items():
                if hasattr(self, key):
                    setattr(self, key, value)

settings = Settings()