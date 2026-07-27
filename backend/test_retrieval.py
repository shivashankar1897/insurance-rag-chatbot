print("1. Starting...")

from src.retrieval.retriever import HybridRetriever

print("2. Imported HybridRetriever")

retriever = HybridRetriever()

print("3. Retriever initialized")

query = "What is the waiting period for pre-existing diseases?"

print("4. Starting hybrid search")

results = retriever.hybrid_search(query)

print("5. Search completed")