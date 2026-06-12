from groq import Groq
from app.config import settings


class GroqService:

    def __init__(self):
        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )

        self.model = settings.LLM_MODEL

    def generate_response(
        self,
        prompt: str
    ):

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    def generate_rag_answer(
        self,
        question: str,
        context: str
    ):

        prompt = f"""
You are an AI Study Assistant.

Context:
{context}

Question:
{question}

Answer only from the provided context.
If information is missing, say so.
"""

        return self.generate_response(prompt)