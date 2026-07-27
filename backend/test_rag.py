from src.pipeline.rag_pipeline import RAGPipeline

rag = RAGPipeline()

question = "What is the waiting period for pre-existing diseases?"

answer = rag.ask(question)

print("=" * 80)
print(question)
print("=" * 80)
print(answer)