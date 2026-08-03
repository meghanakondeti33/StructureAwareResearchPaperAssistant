"""
chunker.py

Creates section-aware chunks.

Author: Meghana
Project: Structure-Aware Multimodal Research Paper Assistant
"""

from typing import List, Dict


class SectionChunker:

    def __init__(self,
                 chunk_size: int = 800,
                 overlap: int = 100):

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_sections(
        self,
        sections: List[Dict]
    ) -> List[Dict]:

        chunks = []

        for section in sections:

            text = section["content"]

            title = section["title"]

            page = section["page"]

            start = 0

            while start < len(text):

                end = start + self.chunk_size

                chunk_text = text[start:end]

                chunks.append({

                    "title": title,

                    "page": page,

                    "content": chunk_text

                })

                start += self.chunk_size - self.overlap

        return chunks