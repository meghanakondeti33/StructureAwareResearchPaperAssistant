"""
chunker.py

Creates structure-aware chunks while preserving
section and page metadata.

Author: Meghana
Project: Structure-Aware Research Paper Assistant
"""

from typing import List, Dict


class SectionChunker:

    def __init__(
        self,
        chunk_size: int = 800,
        overlap: int = 100
    ):

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than 0."
            )

        if overlap < 0:
            raise ValueError(
                "overlap cannot be negative."
            )

        if overlap >= chunk_size:
            raise ValueError(
                "overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    # =========================================================
    # Chunk Sections
    # =========================================================

    def chunk_sections(
        self,
        sections: List[Dict]
    ) -> List[Dict]:

        chunks = []

        step = (
            self.chunk_size
            - self.overlap
        )

        for section in sections:

            text = str(
                section.get(
                    "content",
                    ""
                )
            ).strip()

            title = section.get(
                "title",
                "Unknown Section"
            )

            page = section.get(
                "page",
                0
            )

            # Skip empty sections
            if not text:
                continue

            start = 0

            while start < len(text):

                end = start + self.chunk_size

                chunk_text = text[
                    start:end
                ].strip()

                if chunk_text:

                    chunks.append(
                        {
                            "title": title,
                            "page": page,
                            "content": chunk_text
                        }
                    )

                start += step

        return chunks