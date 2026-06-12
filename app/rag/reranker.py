def rerank_documents(documents):

    ranked_docs = sorted(
        documents,
        key=lambda doc: len(doc.page_content),
        reverse=True
    )

    return ranked_docs