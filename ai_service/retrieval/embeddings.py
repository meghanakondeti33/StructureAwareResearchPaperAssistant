"""
embeddings.py

Generates dense embeddings using BGE.

Author: Meghana
Project: Structure-Aware Multimodal Research Paper Assistant
"""

from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:

    def __init__(
        self,
        model_name="BAAI/bge-small-en-v1.5"
    ):

        print("\nLoading BGE Model...")

        self.model = SentenceTransformer(model_name)

        print("Model Loaded Successfully!")

    def embed_text(self, text):

        return self.model.encode(
            text,
            normalize_embeddings=True
        )

    def embed_chunks(self, chunks):

        texts = [
            chunk["content"]
            for chunk in chunks
        ]

        embeddings = self.model.encode(

            texts,

            batch_size=16,

            show_progress_bar=True,

            normalize_embeddings=True

        )

        return embeddings
