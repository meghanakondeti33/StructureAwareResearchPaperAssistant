"""
vector_store.py

FAISS Vector Store for semantic retrieval.

Author: Meghana
Project: Structure-Aware Multimodal Research Paper Assistant
"""

import faiss
import numpy as np
import os


class VectorStore:

    def __init__(self):

        self.index = None

    # ---------------------------------------------------------
    # Build Index
    # ---------------------------------------------------------

    def build_index(self, embeddings):

        embeddings = np.array(
            embeddings,
            dtype=np.float32
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.index.add(embeddings)

        print(f"\nFAISS Index Built!")

        print(f"Vectors : {self.index.ntotal}")

        print(f"Dimension : {dimension}")

    # ---------------------------------------------------------
    # Save Index
    # ---------------------------------------------------------

    def save_index(
        self,
        path="data/faiss.index"
    ):

        os.makedirs(
            os.path.dirname(path),
            exist_ok=True
        )

        faiss.write_index(
            self.index,
            path
        )

        print(f"Index saved to {path}")

    # ---------------------------------------------------------
    # Load Index
    # ---------------------------------------------------------

    def load_index(
        self,
        path="data/faiss.index"
    ):

        self.index = faiss.read_index(path)

        print(f"Loaded index from {path}")

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    def search(
        self,
        query_embedding,
        top_k=5
    ):

        query_embedding = np.array(
            [query_embedding],
            dtype=np.float32
        )

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        return scores[0], indices[0]
