class Settings(BaseSettings):
    # --- Secrets/Env Vars ---
    # Renamed to API_KEY to match your AWS Secret key and calling code
    API_KEY: str = os.getenv("OPENAI_API_KEY", "") 
    ROUTER_MODEL: str = os.getenv("ROUTER_MODEL", "gpt-4.1-nano")
    SIMPLE_MODEL: str = os.getenv("SIMPLE_MODEL", "gpt-4.1-nano")
    COMPLEX_MODEL: str = os.getenv("COMPLEX_MODEL", "gpt-4.1-mini")
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # --- Paths & Persistence ---
    CHROMA_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    COLLECTION_NAME: str = "tax_docs"

    def __init__(self, **values):
        super().__init__(**values)
        # Only run this in production if the key is still empty
        if os.getenv("ENV") == "prod" and not self.API_KEY:
            aws_secrets = get_aws_secret("prod/tax_assistant/config")
            
            # Map the AWS 'API_KEY' to our self.API_KEY
            if "API_KEY" in aws_secrets:
                self.API_KEY = aws_secrets["API_KEY"]
            
            # Update other models if they exist in the secret
            for key in ["ROUTER_MODEL", "SIMPLE_MODEL", "COMPLEX_MODEL"]:
                if key in aws_secrets:
                    setattr(self, key, aws_secrets[key])