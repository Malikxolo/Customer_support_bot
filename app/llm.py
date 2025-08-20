import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqLLM:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate natural 1-2 line responses"""
        try:
            system_prompt = """You are a helpful customer support bot for food delivery. Keep responses:
            - 1-2 lines maximum
            - Natural and conversational like real customer support
            - Empathetic and solution-focused
            - Professional but friendly
            - Realistic like actual food delivery support agents"""
            
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Groq Error: {e}")
            return "I'm here to help you resolve this issue."

llm = GroqLLM()
