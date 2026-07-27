from openai import AzureOpenAI

from src.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    CHAT_MODEL,
)

from src.pipeline.prompts import (
    SYSTEM_PROMPT,
    USER_PROMPT,
    QUERY_CLASSIFICATION_PROMPT,
)

from src.retrieval.retriever import HybridRetriever
from src.retrieval.policy_detector import detect_policy


client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION,
)


class RAGPipeline:

    def __init__(self):

        self.retriever = HybridRetriever()

    ####################################################################
    # Retrieve Documents
    ####################################################################

    def retrieve(self, query, policy=None):
        """
        Retrieve documents using policy-aware Hybrid Retrieval.
        """

        results = self.retriever.hybrid_search(
            query=query,
            policy=policy,
        )

        docs = []
        seen = set()

        ###############################################################
        # Vector Results
        ###############################################################

        for doc in results["vector"]:

            text = doc["text"]

            if text not in seen:

                docs.append(doc)
                seen.add(text)

        ###############################################################
        # BM25 Results
        ###############################################################

        for doc in results["bm25"]:

            text = doc["text"]

            if text not in seen:

                docs.append(
                    {
                        "text": doc["text"],
                        "metadata": {
                            "source": doc.get("source", ""),
                            "section_name": doc.get("section_name", ""),
                            "plan_name": doc.get("plan_name", ""),
                            "chunk_type": doc.get("chunk_type", ""),
                        },
                    }
                )

                seen.add(text)

        return docs

    ####################################################################
    # Context Builder
    ####################################################################

    def build_context(self, docs):
        """
        Build a clean context for the LLM.

        - Remove duplicate chunks.
        - Prefer Policy Document chunks before Customer Q&A.
        - Limit the context size.
        """

        # Prefer official policy text first
        docs = sorted(
            docs,
            key=lambda d: (
                d["metadata"].get("section_name") != "Policy Document"
            )
        )

        seen = set()
        context_chunks = []

        for doc in docs:

            text = doc["text"].strip()

            if text in seen:
                continue

            seen.add(text)
            context_chunks.append(text)

            # Limit context to top 4 unique chunks
            if len(context_chunks) >= 4:
                break

        return "\n\n".join(context_chunks)

    ####################################################################
    # Query Classification
    ####################################################################

    def classify_query(self, question: str) -> str:

        prompt = QUERY_CLASSIFICATION_PROMPT.format(
            question=question
        )

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "You classify insurance questions.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        return (
            response.choices[0]
            .message.content
            .strip()
            .lower()
        )

    ####################################################################
    # Retrieval Strategy
    ####################################################################

    def retrieve_documents(
        self,
        question: str,
        query_type: str,
        policy: str = None,
    ):

        return self.retrieve(
            question,
            policy=policy,
        )

    ####################################################################
    # Main RAG Pipeline
    ####################################################################

    def ask(self, question):

        ###############################################################
        # Step 1 - Query Classification
        ###############################################################

        query_type = self.classify_query(question)

        ###############################################################
        # Step 2 - Policy Detection
        ###############################################################

        policy = detect_policy(question)

        print("=" * 80)
        print("Detected Policy :", policy)
        print("=" * 80)

        ###############################################################
        # Step 3 - Retrieval
        ###############################################################

        docs = self.retrieve_documents(
            question=question,
            query_type=query_type,
            policy=policy,
        )

        ###############################################################
        # DEBUG: Retrieved Documents
        ###############################################################

        print("\n" + "=" * 80)
        print("DOCUMENTS RETURNED TO RAG")
        print("=" * 80)

        for i, doc in enumerate(docs, 1):

            metadata = doc.get("metadata", {})

            print(f"\n[{i}]")
            print("Policy :", metadata.get("plan_name", ""))
            print("Section:", metadata.get("section_name", ""))
            print(doc["text"][:500])

        ###############################################################
        # Step 4 - Context
        ###############################################################

        context = self.build_context(docs)

        ###############################################################
        # DEBUG: Final Context
        ###############################################################

        print("\n" + "=" * 80)
        print("FINAL CONTEXT SENT TO LLM")
        print("=" * 80)
        print(context[:5000])
        print("=" * 80)

        ###############################################################
        # Step 5 - Prompt
        ###############################################################

        prompt = USER_PROMPT.format(
            question=question,
            context=context,
        )

        ###############################################################
        # DEBUG: Prompt
        ###############################################################

        print("\n" + "=" * 80)
        print("PROMPT SENT TO GPT")
        print("=" * 80)
        print(prompt[:6000])
        print("=" * 80)

        ###############################################################
        # Step 6 - LLM
        ###############################################################

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        ###############################################################
        # Step 7 - Sources
        ###############################################################

        sources = []

        seen_sources = set()

        for doc in docs:

            metadata = doc.get("metadata", {})

            source = {
                "policy": metadata.get("plan_name", ""),
                "section": metadata.get("section_name", ""),
                "source": metadata.get("source", ""),
                "chunk_type": metadata.get("chunk_type", ""),
            }

            key = (
                source["policy"],
                source["section"],
                source["source"],
            )

            if key not in seen_sources:

                sources.append(source)
                seen_sources.add(key)

        ###############################################################
        # Final Response
        ###############################################################

        return {
            "answer": response.choices[0].message.content,
            "sources": sources,
            "query_type": query_type,
            "policy": policy,
        }