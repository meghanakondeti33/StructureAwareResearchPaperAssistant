"""
heading_scorer.py

Analyzes every text span and estimates whether it is
a document heading.

Author: Meghana
Project: Structure-Aware Multimodal Research Paper Assistant
"""

import re


class HeadingScorer:

    def __init__(self):
        pass

    # ----------------------------------------------------
    # Hard Filters
    # ----------------------------------------------------

    def reject(self, text: str) -> bool:

        text = text.strip()

        if not text:
            return True

        # Single integer
        if text.isdigit():
            return True

        # Float
        try:
            float(text)
            return True
        except ValueError:
            pass

        # Email
        if "@" in text:
            return True

        # URL
        if "http" in text.lower():
            return True

        # arXiv metadata
        if text.lower().startswith("arxiv"):
            return True

        # Very long text
        if len(text) > 120:
            return True

        # Single character
        if len(text) <= 1:
            return True

        return False

    # ----------------------------------------------------
    # Heading Score
    # ----------------------------------------------------

    def score(self, element, body_font):

        text = element["text"].strip()
        font = element["font"].lower()
        size = element["font_size"]

        x0, y0, _, _ = element["bbox"]

        score = 0
        reasons = []

        # -------------------------
        # Font Size
        # -------------------------

        if size > body_font:
            score += 3
            reasons.append("Large Font")

        if size > body_font + 4:
            score += 2
            reasons.append("Very Large Font")

        # -------------------------
        # Bold
        # -------------------------

        if "bold" in font or "medi" in font:
            score += 2
            reasons.append("Bold Font")

        # -------------------------
        # Numbered Heading
        # -------------------------

        if re.match(r"^\d+(\.\d+)*", text):
            score += 4
            reasons.append("Numbered Heading")

        # -------------------------
        # Word Count
        # -------------------------

        words = len(text.split())

        if words <= 8:
            score += 2
            reasons.append("Short Heading")

        elif words >= 20:
            score -= 3
            reasons.append("Too Many Words")

        # -------------------------
        # Left Margin
        # -------------------------

        if x0 < 100:
            score += 1
            reasons.append("Left Aligned")

        # -------------------------
        # Near Top
        # -------------------------

        if y0 < 250:
            score += 1
            reasons.append("Top Region")

        # -------------------------
        # Ends with Period
        # -------------------------

        if text.endswith("."):
            score -= 3
            reasons.append("Ends with Period")

        # -------------------------
        # Lowercase Single Word
        # -------------------------

        if text.islower() and words == 1:
            score -= 4
            reasons.append("Lowercase Word")

        return score, reasons

    # ----------------------------------------------------
    # Heading Level
    # ----------------------------------------------------

    def classify_level(self, text):

        if re.match(r"^\d+\.\d+\.\d+", text):
            return 3

        if re.match(r"^\d+\.\d+", text):
            return 2

        if re.match(r"^\d+", text):
            return 1

        return 0

    # ----------------------------------------------------
    # Analyze
    # ----------------------------------------------------

    def analyze(self, element, body_font):

        text = element["text"].strip()

        # Hard rejection
        if self.reject(text):

            return {
                "score": -100,
                "level": -1,
                "reasons": ["Rejected by Hard Filter"]
            }

        score, reasons = self.score(
            element,
            body_font
        )

        level = self.classify_level(text)

        return {

            "score": score,

            "level": level,

            "reasons": reasons

        }
