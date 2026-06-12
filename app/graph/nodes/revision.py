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


def revision_node(state: StudyState):
    docs = state["retrieved_docs"]
    topic = state.get("topic", "the study material")

    if not docs:
        state["revision_plan"] = []
        return state

    context = "\n\n".join(
        f"Source: {doc['document']} (Page {doc['page']}):\n{doc['content']}"
        for doc in docs
    )

    prompt = f"""
You are an expert study planner.
Based on the study context below, generate a 5-day study revision plan for the topic "{topic}".
Provide concrete daily tasks that focus on different parts of the study materials.
You MUST return the output ONLY as a valid JSON list of objects, where each object has exactly:
- "day": integer (1 to 5)
- "task": string (describing the topic and task to study/revise for that day)

Do not include any conversational preamble or postamble.

Context:
{context}

JSON Output:
"""

    groq_service = GroqService()
    try:
        raw_response = groq_service.generate_response(prompt)
        plan = parse_json_list(raw_response)
        state["revision_plan"] = plan
    except Exception as e:
        print(f"Error generating revision plan JSON: {e}")
        state["revision_plan"] = [
            {
                "day": d,
                "task": f"Review section {d} of the {topic} document."
            }
            for d in range(1, 6)
        ]

    return state