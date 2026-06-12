import json
import re
from app.graph.state import StudyState
from app.services.groq_service import GroqService


def parse_json_list(text: str):
    cleaned = text.strip()
    if "```" in cleaned:
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1).strip()
    try:
        return json.loads(cleaned)
    except Exception as e:
        match = re.search(r"(\[.*\])", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
        raise e


def flashcard_node(state: StudyState):
    docs = state["retrieved_docs"]
    topic = state.get("topic", "the study material")

    if not docs:
        state["flashcards"] = []
        return state

    context = "\n\n".join(
        f"Source: {doc['document']} (Page {doc['page']}):\n{doc['content']}"
        for doc in docs
    )

    prompt = f"""
You are an educational study helper.
Based on the study context below, generate a list of 5-8 flashcard question-and-answer pairs for the topic "{topic}".
You MUST return the output ONLY as a valid JSON list of objects, where each object has exactly "question" and "answer" keys.
Do not include any conversational preamble or postamble.

Context:
{context}

JSON Output:
"""

    groq_service = GroqService()
    try:
        raw_response = groq_service.generate_response(prompt)
        flashcards = parse_json_list(raw_response)
        state["flashcards"] = flashcards
    except Exception as e:
        print(f"Error generating flashcards JSON: {e}")
        state["flashcards"] = [
            {
                "question": f"What is a key concept of {topic}?",
                "answer": f"Please refer to the study notes for {topic} to extract this detail."
            }
        ]

    return state