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
    # Span Extraction
    # ---------------------------------------------------------

    def extract_spans(
        self,
        page_number: int
    ) -> List[Dict]:

        layout = self.extract_layout(page_number)

        spans = []

        for block in layout["blocks"]:

            if "lines" not in block:
                continue

            for line in block["lines"]:

                for span in line["spans"]:

                    text = span["text"].strip()

                    if not text:
                        continue

                    spans.append({

                        "page": page_number,

                        "text": text,

                        "font": span["font"],

                        "font_size": span["size"],

                        "bbox": span["bbox"]

                    })

        return spans

    # ---------------------------------------------------------
    # Line Extraction
    # ---------------------------------------------------------

    def extract_lines(
        self,
        page_number: int
    ) -> List[Dict]:

        layout = self.extract_layout(page_number)

        lines = []

        for block in layout["blocks"]:

            if "lines" not in block:
                continue

            for line in block["lines"]:

                line_text = ""

                font_sizes = []

                fonts = []

                bboxes = []

                for span in line["spans"]:

                    text = span["text"].strip()

                    if not text:
                        continue

                    line_text += text + " "

                    font_sizes.append(span["size"])

                    fonts.append(span["font"])

                    bboxes.append(span["bbox"])

                line_text = line_text.strip()

                if not line_text:
                    continue

                # Average font size of the line
                avg_font = (
                    sum(font_sizes) / len(font_sizes)
                    if font_sizes else 0
                )

                # Use first font
                font = fonts[0] if fonts else ""

                # Bounding box of whole line
                x0 = min(b[0] for b in bboxes)
                y0 = min(b[1] for b in bboxes)
                x1 = max(b[2] for b in bboxes)
                y1 = max(b[3] for b in bboxes)

                lines.append({

                    "page": page_number,

                    "text": line_text,

                    "font": font,

                    "font_size": avg_font,

                    "bbox": (x0, y0, x1, y1)

                })

        return lines