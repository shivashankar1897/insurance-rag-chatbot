import pickle
from pathlib import Path

from rank_bm25 import BM25Okapi

from src.ingestion.s3_utils import upload_file


def build_bm25_index(chunks):
    """
    Build a BM25 index from all text chunks.
    """

    print("Building BM25 index...")

    corpus = []

    for chunk in chunks:
        corpus.append(chunk["text"].lower().split())

    bm25 = BM25Okapi(corpus)

    return bm25


def save_bm25_index(
    bm25_index,
    chunks,
    output_dir="./data/indexes",
):
    """
    Save the BM25 index and upload it to S3.
    """

    Path(output_dir).mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = Path(output_dir) / "bm25_index.pkl"

    with open(output_file, "wb") as f:

        pickle.dump(
            {
                "index": bm25_index,
                "chunks": chunks,
            },
            f,
        )

    print(f"BM25 index saved to {output_file}")

    upload_file(
        str(output_file),
        "indexes/bm25_index.pkl",
    )


def load_bm25_index(index_path):
    """
    Load a saved BM25 index.
    """

    with open(index_path, "rb") as f:
        data = pickle.load(f)

    return data["index"], data["chunks"]