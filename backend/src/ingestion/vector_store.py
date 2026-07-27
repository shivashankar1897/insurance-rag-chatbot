from pathlib import Path

import chromadb
from chromadb.config import Settings

from src.config import CHROMA_DB_DIR


COLLECTION_NAME = "insurance_policies"

# Metadata fields that every chunk should contain
REQUIRED_METADATA_FIELDS = [
    "tenant_id",
    "plan_name",
    "section_name",
    "chunk_type",
    "source",
]


def get_chroma_client():
    """
    Create or load the persistent ChromaDB client.
    """
    Path(CHROMA_DB_DIR).mkdir(
        parents=True,
        exist_ok=True,
    )

    return chromadb.PersistentClient(
        path=CHROMA_DB_DIR,
        settings=Settings(anonymized_telemetry=False),
    )


def get_collection():
    """
    Load an existing collection or create it if it doesn't exist.
    """
    client = get_chroma_client()

    try:
        collection = client.get_collection(COLLECTION_NAME)

    except Exception:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={
                "description": "Insurance Policy Knowledge Base"
            },
        )

    return collection


def clear_collection():
    """
    Remove the existing collection and recreate it.
    """
    client = get_chroma_client()

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    return client.create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": "Insurance Policy Knowledge Base"
        },
    )


def store_chunks(chunks):
    """
    Store all chunks and embeddings inside ChromaDB.
    """

    collection = clear_collection()

    ids = []
    documents = []
    embeddings = []
    metadatas = []

    for chunk in chunks:

        metadata = {
            "source": chunk.get("source", ""),
            "tenant_id": chunk.get("tenant_id", ""),
            "plan_name": chunk.get("plan_name", ""),
            "section_name": chunk.get("section_name", ""),
            "chunk_type": chunk.get("chunk_type", ""),
            "document_type": chunk.get("document_type", ""),
            "chunk_number": chunk.get("chunk_number", 0),
        }

        # Warn if any required metadata is missing
        missing = [
            field
            for field in REQUIRED_METADATA_FIELDS
            if not metadata[field]
        ]

        if missing:
            print(
                f"WARNING: Chunk {chunk.get('id')} is missing metadata: {missing}"
            )

        ids.append(chunk["id"])
        documents.append(chunk["text"])
        embeddings.append(chunk["embedding"])
        metadatas.append(metadata)

    # Print one sample for verification
    if chunks:
        print("\n========== SAMPLE CHUNK ==========")
        print(chunks[0])

        print("\n========== SAMPLE METADATA ==========")
        print(metadatas[0])
        print("===================================\n")

    from collections import Counter

    counts = Counter(ids)
    duplicates = {k: v for k, v in counts.items() if v > 1}

    print("\n========== DUPLICATE IDS ==========")
    print(duplicates)
    print("==================================\n")
    
    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"Stored {collection.count()} chunks in ChromaDB")

    return collection


def load_collection():
    """
    Load the persisted ChromaDB collection.
    """
    client = get_chroma_client()

    return client.get_collection(COLLECTION_NAME)