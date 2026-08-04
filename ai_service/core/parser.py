"""
parser.py

Reads a research paper and extracts its structure.

Author: Meghana
Project: Structure-Aware Multimodal Research Paper Assistant
"""

import fitz
from pathlib import Path
from typing import List, Dict


class PDFParser:

    def __init__(self, pdf_path: str):

        self.pdf_path = Path(pdf_path)

        if not self.pdf_path.exists():
            raise FileNotFoundError(
                f"{pdf_path} not found."
            )

        self.document = fitz.open(pdf_path)

    # ---------------------------------------------------------
    # Basic Information
    # ---------------------------------------------------------

    def get_total_pages(self) -> int:
        return len(self.document)

    # ---------------------------------------------------------
    # Raw Page Text
    # ---------------------------------------------------------

    def extract_text(self, page_number: int) -> str:

        page = self.document.load_page(page_number)

        return page.get_text()

    # ---------------------------------------------------------
    # Raw Layout Dictionary
    # ---------------------------------------------------------

    def extract_layout(self, page_number: int) -> Dict:

        page = self.document.load_page(page_number)

        return page.get_text("dict")

    # ---------------------------------------------------------
    # Clean Text Elements
    # ---------------------------------------------------------

    def extract_elements(self) -> List[Dict]:

        elements = []

        for page_num in range(len(self.document)):

            layout = self.extract_layout(page_num)

            for block in layout.get("blocks", []):

                # Ignore non-text blocks (like images)
                if block.get("type") != 0:
                    continue

                for line in block.get("lines", []):

                    for span in line.get("spans", []):

                        text = span["text"].strip()

                        if not text:
                            continue

                        elements.append({

                            "text": text,

                            "font": span["font"],

                            "font_size": round(span["size"], 2),

                            "flags": span["flags"],

                            "color": span["color"],

                            "page": page_num,

                            "bbox": span["bbox"]

                        })

        return elements
