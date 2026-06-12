from typing import TypedDict, List, Dict, Any, Optional


class StudyState(TypedDict):
    # User
    user_id: int

    # Request
    question: str
    topic: str
    action: str

    # Memory
    memory_context: List[Dict[str, Any]]

    # Retrieval
    retrieved_docs: List[Dict[str, Any]]

    # Reranked Results
    reranked_docs: List[Dict[str, Any]]

    # LLM Output
    answer: str

    # Citations
    citations: List[Dict[str, Any]]

    # Generated Content
    summary: str
    flashcards: List[Dict[str, str]]
    quiz: List[Dict[str, Any]]
    revision_plan: List[Dict[str, Any]]

    # Metadata
    document_ids: List[int]
    subject: str
    document_id: Optional[int]

    # Status
    success: bool
    error: Optional[str]