from langchain_chroma import Chroma

from app.rag.embeddings import get_embedding_model
from app.config import settings


def get_vector_store():

    embeddings = get_embedding_model()

    vector_store = Chroma(
        persist_directory=settings.CHROMA_DB_PATH,
        embedding_function=embeddings
    )

    return vector_store


def retrieve_documents(
    query: str,
    user_id: int,
    document_id: int = None,
    k: int = 5
):

    vector_store = get_vector_store()

    conditions = [{"user_id": user_id}]
    if document_id is not None:
        conditions.append({"document_id": document_id})

    if len(conditions) > 1:
        filter_dict = {"$and": conditions}
    else:
        filter_dict = conditions[0]

    docs = vector_store.similarity_search(
        query=query,
        k=k,
        filter=filter_dict
    )

    return docs