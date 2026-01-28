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
    except Exception as e:
        print(f"AWS Secret fallback: {e}")
        return {}

class Settings(BaseSettings):
    # --- Secrets/Env Vars ---
    API_KEY: str = os.getenv("OPENAI_API_KEY", "") 
    ROUTER_MODEL: str = os.getenv("ROUTER_MODEL", "gpt-4o-mini")
    SIMPLE_MODEL: str = os.getenv("SIMPLE_MODEL", "gpt-4o-mini")
    COMPLEX_MODEL: str = os.getenv("COMPLEX_MODEL", "gpt-4o")
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # --- Paths & Persistence ---
    CHROMA_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    COLLECTION_NAME: str = "tax_docs"

    def __init__(self, **values):
        super().__init__(**values)
        # Only load from AWS if explicitly in prod and API_KEY is missing
        if os.getenv("ENV") == "prod" and not self.API_KEY:
            aws_secrets = get_aws_secret("prod/tax_assistant/config")
            if "API_KEY" in aws_secrets:
                self.API_KEY = aws_secrets["API_KEY"]
            # Map other potential keys from AWS
            for key in ["ROUTER_MODEL", "SIMPLE_MODEL", "COMPLEX_MODEL"]:
                if key in aws_secrets:
                    setattr(self, key, aws_secrets[key])

# IMPORTANT: This line MUST exist at the bottom for 'from config import settings' to work
settings = Settings()