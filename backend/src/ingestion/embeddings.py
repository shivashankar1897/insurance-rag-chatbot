from openai import AzureOpenAI

from src.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    EMBED_MODEL,
)


client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION,
)


def generate_embedding(text: str):
    """
    Generate an embedding for a single text chunk.
    """

    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=text,
    )

    return response.data[0].embedding


def generate_embeddings(chunks):
    """
    Generate embeddings for all chunks.
    """

    for chunk in chunks:
        chunk["embedding"] = generate_embedding(chunk["text"])

    return chunks