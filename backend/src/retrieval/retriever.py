import pickle

from openai import AzureOpenAI

from src.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    EMBED_MODEL,
)

from src.ingestion.vector_store import load_collection
from src.retrieval.reranker import CrossEncoderReranker


client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION,
)


class HybridRetriever:

    def __init__(self):

        self.collection = load_collection()

        with open("data/indexes/bm25_index.pkl", "rb") as f:
            data = pickle.load(f)

        self.bm25 = data["index"]
        self.chunks = data["chunks"]

        self.reranker = CrossEncoderReranker()

    ###############################################################
    # Embedding
    ###############################################################

    def embed_query(self, query):

        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=query,
        )

        return response.data[0].embedding

    ###############################################################
    # Vector Search
    ###############################################################

    def vector_search(
        self,
        query,
        policy=None,
        top_k=20,
    ):

        embedding = self.embed_query(query)

        if policy:

            where = {
                "$and": [
                    {"tenant_id": "star-health"},
                    {"plan_name": policy},
                ]
            }

        else:

            where = {
                "tenant_id": "star-health"
            }

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            where=where,
        )

        docs = []

        for i in range(len(results["ids"][0])):

            docs.append(
                {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": results["distances"][0][i],
                }
            )

        return docs

    ###############################################################
    # BM25 Search
    ###############################################################

    def bm25_search(
        self,
        query,
        policy=None,
        top_k=20,
    ):

        scores = self.bm25.get_scores(
            query.lower().split()
        )

        ranked = sorted(
            zip(scores, self.chunks),
            reverse=True,
            key=lambda x: x[0],
        )

        results = []

        for score, chunk in ranked:

            if policy:

                if chunk.get("plan_name", "").lower() != policy.lower():
                    continue

            chunk_copy = chunk.copy()
            chunk_copy["bm25_score"] = float(score)

            results.append(chunk_copy)

            if len(results) >= top_k:
                break

        return results

    ###############################################################
    # Hybrid Search
    ###############################################################

    def hybrid_search(
        self,
        query,
        policy=None,
        top_k=5,
    ):

        print(f"\nDetected policy: {policy}")
        ############################################################
        # VECTOR SEARCH
        ############################################################

        vector_docs = self.vector_search(
            query=query,
            policy=policy,
            top_k=20,
        )

        print("\n" + "=" * 80)
        print("VECTOR SEARCH RESULTS")
        print("=" * 80)

        for i, doc in enumerate(vector_docs, 1):
            print(f"\n[{i}]")
            print(f"Distance : {doc.get('score')}")
            print(f"Policy   : {doc['metadata'].get('plan_name', '')}")
            print(f"Section  : {doc['metadata'].get('section_name', '')}")
            print(doc["text"][:400])

        ############################################################
        # BM25 SEARCH
        ############################################################

        bm25_docs = self.bm25_search(
            query=query,
            policy=policy,
            top_k=20,
        )

        print("\n" + "=" * 80)
        print("BM25 RESULTS")
        print("=" * 80)

        for i, doc in enumerate(bm25_docs, 1):
            print(f"\n[{i}]")
            print(f"Score    : {doc.get('bm25_score')}")
            print(f"Policy   : {doc.get('plan_name', '')}")
            print(f"Section  : {doc.get('section_name', '')}")
            print(doc["text"][:400])

        ############################################################
        # MERGE RESULTS
        ############################################################

        merged_docs = []
        seen = set()

        for doc in vector_docs:

            key = doc["text"].strip()

            if key in seen:
                continue

            merged_docs.append(doc)
            seen.add(key)

        for doc in bm25_docs:

            key = doc["text"].strip()

            if key in seen:
                continue

            merged_docs.append(
                {
                    "text": doc["text"],
                    "metadata": {
                        "plan_name": doc.get("plan_name", ""),
                        "source": doc.get("source", ""),
                        "section_name": doc.get("section_name", ""),
                        "chunk_type": doc.get("chunk_type", ""),
                    },
                    "score": doc.get("bm25_score", 0),
                }
            )

            seen.add(key)
        
        ############################################################
        # RERANK
        ############################################################

        reranked_docs = self.reranker.rerank(
            query=query,
            docs=merged_docs,
            top_k=20,
        )

        # FILTER DOCUMENTS BY DETECTED POLICY
        if policy:

            filtered_docs = []

            for doc in reranked_docs:

                metadata = doc.get("metadata", {})
                text = doc["text"].lower()

                policy_lower = policy.lower() if policy else ""
                # Reject chunks that explicitly mention another policy
                other_policies = [
                    "star comprehensive",
                    "star senior citizen",
                    "bajaj health guard",
                    "hdfc ergo",
                ]

                wrong_policy = False

                for p in other_policies:
                    if p != policy_lower and p in text:
                        wrong_policy = True
                        break

                if wrong_policy:
                    continue

                # Keep if metadata matches detected policy
                if metadata.get("plan_name", "").lower() == policy_lower:
                    filtered_docs.append(doc)
                    continue

                # Keep if the text explicitly mentions the detected policy
                if policy_lower in text:
                    filtered_docs.append(doc)
                    continue

                # Always keep official policy document sections
                if metadata.get("source") == "star_health_comprehensive_policy.docx":
                    filtered_docs.append(doc)

            if filtered_docs:
                reranked_docs = filtered_docs

        # ------------------------------------------------------------------
        # Preserve ALL matching Policy Document chunks
        # ------------------------------------------------------------------

        policy_docs = []

        for doc in merged_docs:

            metadata = doc.get("metadata", {})

            if (
                policy
                and metadata.get("section_name") == "Policy Document"
                and metadata.get("plan_name", "").lower() == policy.lower()
            ):
                policy_docs.append(doc)

        print("\n===== POLICY DOCUMENT CHUNKS =====")

        for i, doc in enumerate(policy_docs, 1):
            print(f"\nPolicy Chunk {i}")
            print(doc["text"][:300])

        # Remove any Policy Document chunks already present
        reranked_docs = [
            d for d in reranked_docs
            if d.get("metadata", {}).get("section_name") != "Policy Document"
        ]

        # Keep up to the first two Policy Document chunks
        policy_docs = policy_docs[:2]

        # Prepend them before the reranked results
        reranked_docs = policy_docs + reranked_docs

        
        ############################################################
        # KEEP ONLY TOP K
        ############################################################

        reranked_docs = reranked_docs[:top_k]
        
        print("\n" + "=" * 80)
        print("RERANKED RESULTS")
        print("=" * 80)

        for i, doc in enumerate(reranked_docs, 1):

            metadata = doc.get("metadata", {})

            print(f"\n[{i}]")
            print(f"Policy   : {metadata.get('plan_name', '')}")
            print(f"Section  : {metadata.get('section_name', '')}")
            print(doc["text"][:400])

        return {
            "vector": reranked_docs,
            "bm25": [],
        }