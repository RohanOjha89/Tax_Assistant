from openai import OpenAI
from config import settings

class SemanticRouter:
    def __init__(self):
        # API_KEY and ROUTER_MODEL now come from AWS Secrets via Settings
        self.client = OpenAI(api_key=settings.API_KEY)

    def classify_query(self, query: str) -> str:
        """
        Classifies the user query to decide which LLM to use.
        """
        prompt = f"""You are a specialized routing assistant for a Tax AI. 
        Classify the query below into exactly one of two categories: 'SIMPLE' or 'COMPLEX'.
        
        SIMPLE: Definitions, general rules, or document lookups.
        Examples: "What is 80C?", "Standard deduction limit", "TDS on salary".
        
        COMPLEX: Mathematical calculations, tax planning, comparative analysis, or specific scenarios.
        Examples: "Calculate tax for 12L income", "Old vs New regime for me", "Penalty for late filing".

        Query: {query}
        
        Output only the word 'SIMPLE' or 'COMPLEX' without punctuation or explanation."""
        
        response = self.client.chat.completions.create(
            model=settings.ROUTER_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that only outputs one word: SIMPLE or COMPLEX."},
                {"role": "user", "content": prompt}
            ],
            temperature=0  # Keep it deterministic
        )
        
        result = response.choices[0].message.content.strip().upper()
        
        # Fallback guardrail
        return "COMPLEX" if "COMPLEX" in result else "SIMPLE"