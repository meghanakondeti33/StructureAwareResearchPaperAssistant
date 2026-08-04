"""
section_detector.py

Detects section headings using the HeadingScorer.

Author: Meghana
Project: Structure-Aware Multimodal Research Paper Assistant
"""

from collections import Counter
try:
    from src.core.heading_scorer import HeadingScorer
except ImportError:
    from ai_service.core.heading_scorer import HeadingScorer


class SectionDetector:

    def __init__(self, threshold=5):
        """
        threshold:
            Minimum score required for a text span
            to be considered a heading.
        """

        self.threshold = threshold
        self.scorer = HeadingScorer()

    def detect_sections(self, elements):

        # ---------------------------------------------------
        # Estimate Body Font
        # ---------------------------------------------------

        fonts = [
            element["font_size"]
            for element in elements
        ]

        if not fonts:
            body_font = 10.0
        else:
            body_font = Counter(fonts).most_common(1)[0][0]

        headings = []

        # ---------------------------------------------------
        # Analyze Every Element
        # ---------------------------------------------------

        for element in elements:

            analysis = self.scorer.analyze(
                element,
                body_font
            )

            score = analysis["score"]

            level = analysis["level"]

            if score >= self.threshold:

                headings.append({

                    "title": element["text"],

                    "page": element["page"],

                    "level": level,

                    "score": score,

                    "bbox": element["bbox"],

                    "font": element["font"],

                    "font_size": element["font_size"]

                })

        return headings
