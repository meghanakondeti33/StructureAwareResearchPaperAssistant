"""
vector_store.py

FAISS Vector Store for semantic retrieval.

Author: Meghana
Project: Structure-Aware Research Paper Assistant
"""

from pathlib import Path

import faiss
import numpy as np


class VectorStore:

    def __init__(self):
        self.index = None

    # ---------------------------------------------------------
    # Build Index
    # ---------------------------------------------------------

    def build_index(self, embeddings):
        """
        Build a FAISS index from document embeddings.

        Normalized embeddings + Inner Product
        = cosine similarity.
        """

        if embeddings is None:
            raise ValueError(
                "Embeddings cannot be None."
            )

        embeddings = np.asarray(
            embeddings,
            dtype=np.float32
        )

        if embeddings.ndim != 2:
            raise ValueError(
                f"Expected 2D embeddings, "
                f"got shape {embeddings.shape}"
            )

        if embeddings.shape[0] == 0:
            raise ValueError(
                "Cannot build FAISS index from empty embeddings."
            )

        # Normalize document vectors.
        faiss.normalize_L2(embeddings)

        dimension = embeddings.shape[1]

        # Inner Product on normalized vectors
        # is equivalent to cosine similarity.
        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.index.add(
            embeddings
        )

        print("\nFAISS Index Built Successfully!")
        print(f"Vectors   : {self.index.ntotal}")
        print(f"Dimension : {dimension}")

        return self.index

    # ---------------------------------------------------------
    # Create Index Alias
    # ---------------------------------------------------------

    def create_index(self, embeddings):
        """
        Compatibility alias for build_index().
        """

        return self.build_index(embeddings)

    # ---------------------------------------------------------
    # Add Embeddings
    # ---------------------------------------------------------

    def add_embeddings(self, embeddings):

        if self.index is None:
            return self.build_index(embeddings)

        embeddings = np.asarray(
            embeddings,
            dtype=np.float32
        )

        if embeddings.ndim != 2:
            raise ValueError(
                f"Expected 2D embeddings, "
                f"got shape {embeddings.shape}"
            )

        faiss.normalize_L2(
            embeddings
        )

        self.index.add(
            embeddings
        )

        return self.index

    # ---------------------------------------------------------
    # Save Index
    # ---------------------------------------------------------

    def save_index(
        self,
        path="data/faiss.index"
    ):

        if self.index is None:
            raise RuntimeError(
                "Cannot save FAISS index because it is empty."
            )

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        faiss.write_index(
            self.index,
            str(path)
        )

        print(
            f"FAISS index saved to {path}"
        )

    # ---------------------------------------------------------
    # Load Index
    # ---------------------------------------------------------

    def load_index(
        self,
        path="data/faiss.index"
    ):

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {path}"
            )

        self.index = faiss.read_index(
            str(path)
        )

        print(
            "FAISS index loaded successfully!"
        )

        print(
            f"Vectors : {self.index.ntotal}"
        )

        return self.index

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    def search(
        self,
        query_embedding,
        top_k=5
    ):

        if self.index is None:
            raise RuntimeError(
                "FAISS index has not been loaded or created."
            )

        query_embedding = np.asarray(
            query_embedding,
            dtype=np.float32
        )

        # Accept:
        # (dimension,)
        # OR
        # (1, dimension)

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(
                1,
                -1
            )

        if query_embedding.ndim != 2:
            raise ValueError(
                f"Invalid query embedding shape: "
                f"{query_embedding.shape}"
            )

        # Normalize query vector.
        faiss.normalize_L2(
            query_embedding
        )

        k = min(
            int(top_k),
            self.index.ntotal
        )

        if k <= 0:
            return (
                np.array([], dtype=np.float32),
                np.array([], dtype=np.int64)
            )

        scores, indices = self.index.search(
            query_embedding,
            k
        )

        return (
            scores[0],
            indices[0]
        )

    # ---------------------------------------------------------
    # Number of Vectors
    # ---------------------------------------------------------

    def size(self):

        if self.index is None:
            return 0

        return self.index.ntotal