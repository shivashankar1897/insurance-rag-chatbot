from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas import (
    ChatRequest,
    ChatResponse,
)

from src.guardrails.validators import check_input
from src.pipeline.rag_pipeline import RAGPipeline


app = FastAPI(
    title="Insurance RAG API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


rag = RAGPipeline()


@app.get("/")
def home():

    return {
        "message": "Insurance RAG API Running"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    # -----------------------------
    # Phase 1: Input Guardrails
    # -----------------------------
    is_safe, reason, message = check_input(
        request.question
    )

    if not is_safe:

        return ChatResponse(
            answer=message,
            sources=[],
        )

    # -----------------------------
    # RAG Pipeline
    # -----------------------------
    result = rag.ask(request.question)

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
    )