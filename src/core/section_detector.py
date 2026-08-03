"""
section_detector.py

Detects section headings using the HeadingScorer.

Author: Meghana
Project: Structure-Aware Multimodal Research Paper Assistant
"""

from collections import Counter
from src.core.heading_scorer import HeadingScorer


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

        font_sizes = [
            round(e["font_size"])
            for e in elements
        ]

        body_font = Counter(font_sizes).most_common(1)[0][0]

        headings = []

        print("\n")
        print("=" * 120)
        print("Heading Detection")
        print("=" * 120)

        print(
            f"{'Score':<8}"
            f"{'Page':<8}"
            f"{'Decision':<10}"
            f"{'Level':<8}"
            f"Heading"
        )

        print("-" * 120)

        # ---------------------------------------------------
        # Analyze every span
        # ---------------------------------------------------

        for element in elements:

            result = self.scorer.analyze(
                element,
                body_font
            )

            score = result["score"]

            # Decision is made HERE
            decision = score >= self.threshold

            if decision:

                headings.append({

                    "title": element["text"].strip(),

                    "page": element["page"],

                    "font_size": element["font_size"],

                    "bbox": element["bbox"],

                    "level": result["level"],

                    "score": score,

                    "reasons": result["reasons"]

                })

            # Print useful debug information
            if score >= 3 or score <= -5:

                print(
                    f"{score:<8}"
                    f"{element['page'] + 1:<8}"
                    f"{'YES' if decision else 'NO':<10}"
                    f"{result['level']:<8}"
                    f"{element['text']}"
                )

                print(
                    " " * 32 +
                    "Reasons : " +
                    ", ".join(result["reasons"])
                )

                print("-" * 120)

        print("\n")
        print("=" * 120)
        print(f"Detected Headings : {len(headings)}")
        print("=" * 120)

        return headings