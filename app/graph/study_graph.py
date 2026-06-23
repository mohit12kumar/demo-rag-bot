from langgraph.graph import StateGraph, END

from app.graph.state import StudyState

from app.graph.nodes.memory import memory_node
from app.graph.nodes.retrieve import retrieve_node
from app.graph.nodes.summarize import summarize_node
from app.graph.nodes.flashcard import flashcard_node
from app.graph.nodes.quiz import quiz_node
from app.graph.nodes.revision import revision_node
from app.services.groq_service import GroqService



# =====================================
# Router Node
# =====================================

def router_node(state: StudyState):

    # If action is already explicitly specified (e.g. from a direct API route), preserve it
    if state.get("action"):
        return state

    question = state["question"].lower()

    if "summary" in question or "summarize" in question:
        state["action"] = "summary"

    elif "flashcard" in question:
        state["action"] = "flashcard"

    elif "quiz" in question:
        state["action"] = "quiz"

    elif "revision" in question:
        state["action"] = "revision"

    else:
        state["action"] = "qa"

    return state



# =====================================
# QA Node
# =====================================

def qa_node(state: StudyState):

    docs = state["retrieved_docs"]

    if not docs:
        state["answer"] = "No relevant study materials found. Please upload notes, PDFs, or YouTube transcripts first."
        return state

    context = "\n\n".join(
        f"Source: {doc['document']} (Page/Slide {doc['page']}):\n{doc['content']}"
        for doc in docs
    )

    groq_service = GroqService()
    try:
        answer = groq_service.generate_rag_answer(
            question=state["question"],
            context=context
        )
        state["answer"] = answer
    except Exception as e:
        state["answer"] = f"Error generating answer from LLM: {str(e)}"

    return state


# =====================================
# Conditional Router
# =====================================

def route_action(state: StudyState):

    action = state["action"]

    if action == "summary":
        return "summary"

    if action == "flashcard":
        return "flashcard"

    if action == "quiz":
        return "quiz"

    if action == "revision":
        return "revision"

    return "qa"


# =====================================
# Build Workflow
# =====================================

workflow = StateGraph(StudyState)

# Nodes
workflow.add_node("router", router_node)
workflow.add_node("memory", memory_node)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("qa", qa_node)
workflow.add_node("summary", summarize_node)
workflow.add_node("flashcard", flashcard_node)
workflow.add_node("quiz", quiz_node)
workflow.add_node("revision", revision_node)

# Entry Point
workflow.set_entry_point("router")

# Flow
workflow.add_edge("router", "memory")
workflow.add_edge("memory", "retrieve")

workflow.add_conditional_edges(
    "retrieve",
    route_action,
    {
        "qa": "qa",
        "summary": "summary",
        "flashcard": "flashcard",
        "quiz": "quiz",
        "revision": "revision",
    }
)

workflow.add_edge("qa", END)
workflow.add_edge("summary", END)
workflow.add_edge("flashcard", END)
workflow.add_edge("quiz", END)
workflow.add_edge("revision", END)

# Compile Graph
study_graph = workflow.compile()


# =====================================
# Helper Function
# =====================================

def run_study_graph(
    question: str,
    user_id: int,
    action: str = "",
    document_id: int = None,
    topic: str = ""
):

    initial_state = {
        "user_id": user_id,
        "question": question,
        "action": action,
        "topic": topic,
        "document_id": document_id,
        "memory_context": [],
        "retrieved_docs": [],
        "citations": [],
        "answer": "",
        "summary": "",
        "flashcards": [],
        "quiz": [],
        "revision_plan": [],
        "document_ids": [],
        "subject": "",
        "success": True,
        "error": None
    }

    return study_graph.invoke(initial_state)