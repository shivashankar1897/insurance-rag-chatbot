from typing import List, Dict

from langchain_text_splitters import RecursiveCharacterTextSplitter


# Standard chunking configuration
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        "",
    ],
)


def chunk_text_document(document: Dict) -> List[Dict]:
    """
    Chunk text-based documents such as PDF, DOCX and TXT.
    """

    chunks = text_splitter.split_text(document["text"])

    results = []

    for i, chunk in enumerate(chunks):

        results.append(
            {
                "id": f"{document['source']}_{i}",
                "text": chunk,
                "source": document["source"],
                "tenant_id": document["tenant_id"],
                "plan_name": document["plan_name"],
                "section_name": document["section_name"],
                "chunk_number": i,
                "chunk_type": "policy_text",
                "document_type": document["type"],
            }
        )

    return results


def chunk_table_document(document: Dict) -> List[Dict]:
    """
    Chunk CSV/XLSX documents.

    CSV parser already returns one document per row,
    so create exactly one chunk for each document.
    """

    return [
        {
            "id": f"{document['source']}_{document['row_number']}",
            "text": document["text"],
            "source": document["source"],
            "tenant_id": document["tenant_id"],
            "plan_name": document["plan_name"],
            "section_name": document["section_name"],
            "chunk_number": document["row_number"],
            "chunk_type": "table",
            "document_type": document["type"],
        }
    ]

def chunk_documents(documents: List[Dict]) -> List[Dict]:
    """
    Chunk all loaded documents.
    """

    all_chunks = []

    for document in documents:

        # Validate required metadata
        required_fields = [
            "tenant_id",
            "plan_name",
            "section_name",
        ]

        missing = [
            field
            for field in required_fields
            if not document.get(field)
        ]

        if missing:
            raise ValueError(
                f"Document '{document['source']}' is missing required metadata: {missing}"
            )

        if document["type"] in ["pdf", "docx", "txt"]:
            all_chunks.extend(
                chunk_text_document(document)
            )

        elif document["type"] in ["csv", "xlsx"]:
            all_chunks.extend(
                chunk_table_document(document)
            )

    return all_chunks