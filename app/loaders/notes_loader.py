from langchain_core.documents import Document


def load_notes(file_path: str):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        text = file.read()

    documents = [
        Document(
            page_content=text,
            metadata={
                "source": file_path
            }
        )
    ]

    return documents