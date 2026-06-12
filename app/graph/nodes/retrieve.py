import re
from app.graph.state import StudyState
from app.rag.retriever import retrieve_documents
from app.database.mysql import SessionLocal
from app.database.models import Document as DBDocument


def retrieve_node(state: StudyState):
    question = state["question"]
    user_id = state["user_id"]
    document_id = state.get("document_id")

    # 1. Retrieve matching chunks from ChromaDB
    retrieved_langchain_docs = []
    try:
        retrieved_langchain_docs = retrieve_documents(
            query=question,
            user_id=user_id,
            document_id=document_id,
            k=6
        )
    except Exception as e:
        print(f"Error querying ChromaDB: {e}")

    # Convert langchain documents to serialized dictionary format for StudyState
    docs = []
    for doc in retrieved_langchain_docs:
        docs.append({
            "content": doc.page_content,
            "document": doc.metadata.get("source", "Uploaded Document"),
            "page": doc.metadata.get("page", 1)
        })

    # 2. Meta-query handling (e.g. "What have I learned so far in this course?")
    # Check if the query asks about overall progress, syllabus, course content, or uploads
    normalized_question = question.lower()
    meta_keywords = [
        "what have i learned", "what did i learn", "what have i covered", 
        "what did i cover", "so far in this course", "what have i uploaded", 
        "what documents do i have", "my course so far", "what topics",
        "learned so far", "what files"
    ]
    
    is_meta_query = any(kw in normalized_question for kw in meta_keywords)
    
    if is_meta_query:
        db = SessionLocal()
        try:
            # Query MySQL for all documents in this user context
            query = db.query(DBDocument).filter(DBDocument.user_id == user_id)
            
            db_docs = query.all()
            if db_docs:
                doc_list_str = ", ".join([f"'{d.document_name}' ({d.document_type})" for d in db_docs])
                meta_content = (
                    f"System Metadata Context: The user has uploaded and studied the following "
                    f"documents in this course/subject: [{doc_list_str}]. Use this list to summarize "
                    f"their overall progress and topics learned so far."
                )
                # Append this virtual chunk at the beginning of the retrieval context
                docs.insert(0, {
                    "content": meta_content,
                    "document": "Course Syllabus / Uploaded Notes",
                    "page": 1
                })
        except Exception as db_err:
            print(f"Error reading DB docs for meta-query: {db_err}")
        finally:
            db.close()

    # 3. Populate state
    state["retrieved_docs"] = docs
    state["citations"] = [
        {
            "document": doc["document"],
            "page": doc["page"]
        }
        for doc in docs
    ]

    return state