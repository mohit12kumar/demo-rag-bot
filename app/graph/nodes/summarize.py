from app.graph.state import StudyState
from app.services.groq_service import GroqService


def summarize_node(state: StudyState):
    docs = state["retrieved_docs"]
    topic = state.get("topic", "the study material")

    if not docs:
        state["summary"] = f"No relevant materials found to generate a summary for '{topic}'."
        return state

    context = "\n\n".join(
        f"Source: {doc['document']} (Page {doc['page']}):\n{doc['content']}"
        for doc in docs
    )

    prompt = f"""
You are an expert AI Academic Tutor.
Generate a comprehensive, clear, and highly structured summary for the topic: "{topic}" using the provided study context.
Make sure to explain core concepts, outline key definitions, and structure it using bold points and clean bullet lists.

Context:
{context}

Summary:
"""

    groq_service = GroqService()
    try:
        summary = groq_service.generate_response(prompt)
        state["summary"] = summary.strip()
    except Exception as e:
        state["summary"] = f"Error generating summary: {str(e)}"

    return state