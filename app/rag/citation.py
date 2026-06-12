def generate_citations(documents):

    citations = []

    for doc in documents:

        citations.append(
            {
                "document":
                    doc.metadata.get(
                        "source",
                        "Unknown"
                    ),

                "page":
                    doc.metadata.get(
                        "page",
                        "N/A"
                    )
            }
        )

    return citations