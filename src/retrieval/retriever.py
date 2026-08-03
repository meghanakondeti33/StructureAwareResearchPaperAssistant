"""
retriever.py

Semantic Retriever using BGE + FAISS.

Author: Meghana
Project: Structure-Aware Multimodal Research Paper Assistant
"""

from src.retrieval.embeddings import EmbeddingGenerator
from src.retrieval.vector_store import VectorStore


class Retriever:

    def __init__(self):

        self.embedder = EmbeddingGenerator()

        self.vector_store = VectorStore()

    # ---------------------------------------------------------
    # Load Existing FAISS Index
    # ---------------------------------------------------------

    def load(self, index_path="data/faiss.index"):

        self.vector_store.load_index(index_path)

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    def retrieve(
        self,
        query,
        chunks,
        top_k=5
    ):

        query_embedding = self.embedder.embed_text(query)

        scores, indices = self.vector_store.search(
            query_embedding,
            top_k
        )

        results = []

        for score, idx in zip(scores, indices):

            results.append({

                "score": float(score),

                "chunk": chunks[idx]

            })

        return results