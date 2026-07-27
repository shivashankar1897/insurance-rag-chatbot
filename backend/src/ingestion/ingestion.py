import json
from pathlib import Path

from src.ingestion.s3_utils import (
    download_folder,
    upload_file,
)

from src.ingestion.parsers import load_documents
from src.ingestion.chunking import chunk_documents
from src.ingestion.embeddings import generate_embeddings
from src.ingestion.vector_store import store_chunks
from src.ingestion.bm25_index import (
    build_bm25_index,
    save_bm25_index,
)


class IngestionPipeline:
    """
    Complete ingestion pipeline.
    """

    def __init__(self):

        self.documents = []
        self.chunks = []

        self.raw_folder = "./data/raw"
        self.processed_folder = "./data/processed"

    def download(self):

        print("\nDownloading raw documents from S3...")

        download_folder(
            prefix="raw/",
            local_folder=self.raw_folder,
        )

    def parse(self):

        print("\nLoading documents...")

        self.documents = load_documents(
            self.raw_folder
        )

        print(f"Loaded {len(self.documents)} documents")

    def chunk(self):

        print("\nChunking documents...")

        self.chunks = chunk_documents(
            self.documents
        )

        print(f"Created {len(self.chunks)} chunks")

    def embed(self):

        print("\nGenerating embeddings...")

        self.chunks = generate_embeddings(
            self.chunks
        )

    def create_vector_store(self):

        print("\nCreating ChromaDB...")

        store_chunks(
            self.chunks
        )

    def create_bm25(self):

        print("\nCreating BM25 index...")

        bm25 = build_bm25_index(
            self.chunks
        )

        save_bm25_index(
            bm25,
            self.chunks,
        )

    def save_chunks(self):

        print("\nSaving processed chunks...")

        Path(self.processed_folder).mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            Path(self.processed_folder)
            / "all_chunks.json"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                self.chunks,
                f,
                indent=2,
                ensure_ascii=False,
            )

        upload_file(
            str(output_file),
            "processed/all_chunks.json",
        )

    def run(self):

        self.download()

        self.parse()

        self.chunk()

        self.embed()

        self.create_vector_store()

        self.create_bm25()

        self.save_chunks()

        print("\n" + "=" * 50)
        print("INGESTION COMPLETED SUCCESSFULLY")
        print("=" * 50)

        print(f"Documents : {len(self.documents)}")
        print(f"Chunks    : {len(self.chunks)}")

        return self.chunks


if __name__ == "__main__":

    pipeline = IngestionPipeline()

    pipeline.run()