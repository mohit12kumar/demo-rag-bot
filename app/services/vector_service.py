from langchain_chroma import Chroma

from app.rag.embeddings import (
    get_embedding_model
)
from app.config import settings


class VectorService:

    def __init__(self):

        self.vector_store = Chroma(
            persist_directory=settings.CHROMA_DB_PATH,
            embedding_function=get_embedding_model()
        )

    def add_documents(
        self,
        documents
    ):

        return self.vector_store.add_documents(
            documents
        )

    def similarity_search(
        self,
        query: str,
        k: int = 5
    ):

        docs = self.vector_store.similarity_search(
            query=query,
            k=k
        )

        return docs

    def delete_collection(self):

        self.vector_store.delete_collection()