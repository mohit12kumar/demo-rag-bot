from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings


def chunk_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = splitter.split_documents(documents)

    return chunks