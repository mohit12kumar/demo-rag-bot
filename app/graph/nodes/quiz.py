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


def quiz_node(state: StudyState):
    docs = state["retrieved_docs"]
    topic = state.get("topic", "the study material")

    if not docs:
        state["quiz"] = []
        return state

    context = "\n\n".join(
        f"Source: {doc['document']} (Page {doc['page']}):\n{doc['content']}"
        for doc in docs
    )

    prompt = f"""
You are an expert examiner.
Based on the study context below, generate a multiple-choice quiz of 5 questions about the topic "{topic}".
Each question must have exactly 4 options and a correct answer which must match one of the options.
You MUST return the output ONLY as a valid JSON list of objects, where each object has exactly these keys:
- "question": string
- "options": list of exactly 4 strings
- "answer": string (which MUST match exactly one of the options)

Do not include any conversational preamble or postamble.

Context:
{context}

JSON Output:
"""

    groq_service = GroqService()
    try:
        raw_response = groq_service.generate_response(prompt)
        quiz = parse_json_list(raw_response)
        state["quiz"] = quiz
    except Exception as e:
        print(f"Error generating quiz JSON: {e}")
        state["quiz"] = [
            {
                "question": f"What is a main concept in {topic}?",
                "options": ["FastAPI", "Python", "Git", "All of the above"],
                "answer": "All of the above"
            }
        ]

    return state