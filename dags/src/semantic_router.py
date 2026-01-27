from openai import OpenAI
from config import API_KEY, ROUTER_MODEL
from dotenv import load_dotenv

class SemanticRouter:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY)

    def classify_query(self, query):
        prompt = f"""Classify the following user query as 'SIMPLE' or 'COMPLEX'.
        SIMPLE: Factual questions, definitions, explanations, lookups
        Examples: "What is Section 80C?", "Define capital gains", "Explain TDS"
        
        COMPLEX: Calculations, comparisons, analysis, scenarios, penalties
        Examples: "Calculate tax for ₹15L income", "Compare tax regimes", 
                  "Penalty for late filing", "Which option do you think is better?"
                  
        Query: {query}
        Output only the word 'SIMPLE' or 'COMPLEX'."""
        
        response = self.client.chat.completions.create(model=ROUTER_MODEL, messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content.strip().upper()