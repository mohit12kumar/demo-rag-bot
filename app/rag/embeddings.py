from langchain_community.embeddings import HuggingFaceEmbeddings

from app.config import settings


def get_embedding_model():

    embeddings = HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL
    )

    return embeddings