from sentence_transformers import CrossEncoder


class CrossEncoderReranker:
    """
    Rerank retrieved documents using a CrossEncoder model.
    """

    def __init__(self):

        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def rerank(
        self,
        query,
        docs,
        top_k=5,
    ):
        """
        Rerank retrieved documents.
        """

        if not docs:
            return []

        pairs = [
            (query, doc["text"])
            for doc in docs
        ]

        scores = self.model.predict(pairs)

        ranked_docs = sorted(
            zip(scores, docs),
            key=lambda x: x[0],
            reverse=True,
        )

        return [
            doc
            for _, doc in ranked_docs[:top_k]
        ]