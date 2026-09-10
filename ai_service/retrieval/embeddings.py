"""
embeddings.py

Generates dense embeddings using BGE.

Author: Meghana
Project: Structure-Aware Research Paper Assistant
"""

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:

    def __init__(
        self,
        model_name="BAAI/bge-small-en-v1.5"
    ):
        print("\nLoading BGE Model...")
        print(f"Model: {model_name}")

        self.model = SentenceTransformer(model_name)

        self.dimension = (
            self.model.get_sentence_embedding_dimension()
        )

        print(
            f"Model Loaded Successfully! "
            f"Dimension: {self.dimension}"
        )

    # ---------------------------------------------------------
    # Embed User Query
    # ---------------------------------------------------------

    def embed_text(self, text):

        if not text or not text.strip():
            raise ValueError(
                "Cannot create embedding for empty text."
            )

        # BGE retrieval query instruction
        query = (
            "Represent this sentence for searching relevant passages: "
            + text.strip()
        )

        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        return np.asarray(
            embedding,
            dtype=np.float32
        )

    # ---------------------------------------------------------
    # Embed Document Chunks
    # ---------------------------------------------------------

    def embed_chunks(self, chunks):

        if not chunks:
            raise ValueError(
                "No chunks provided for embedding."
            )

        texts = [
            chunk["content"].strip()
            for chunk in chunks
            if chunk.get("content", "").strip()
        ]

        if not texts:
            raise ValueError(
                "No valid chunk content found."
            )

        embeddings = self.model.encode(
            texts,
            batch_size=16,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return np.asarray(
            embeddings,
            dtype=np.float32
        )

    # ---------------------------------------------------------
    # Get Embedding Dimension
    # ---------------------------------------------------------

    def get_dimension(self):
        return self.dimension