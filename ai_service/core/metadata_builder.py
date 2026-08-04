"""
metadata_builder.py

Builds logical document sections from detected headings.

Author: Meghana
Project: Structure-Aware Multimodal Research Paper Assistant
"""

from typing import List, Dict


class MetadataBuilder:

    def __init__(self):
        pass

    def build_sections(
        self,
        elements: List[Dict],
        headings: List[Dict]
    ) -> List[Dict]:

        sections = []

        # No headings found
        if not headings:
            return sections

        # Sort headings by page and y-position
        headings = sorted(
            headings,
            key=lambda h: (
                h["page"],
                h["bbox"][1]
            )
        )

        for i, heading in enumerate(headings):

            current_page = heading["page"]

            current_y = heading["bbox"][1]

            # Find next heading
            if i < len(headings) - 1:

                next_page = headings[i + 1]["page"]

                next_y = headings[i + 1]["bbox"][1]

            else:

                next_page = float("inf")

                next_y = float("inf")

            content = []

            for element in elements:

                page = element["page"]

                y = element["bbox"][1]

                text = element["text"].strip()

                if not text:
                    continue

                # Skip the heading itself
                if text == heading["title"]:
                    continue

                # Same page
                if current_page == next_page:

                    if (
                        page == current_page
                        and current_y < y < next_y
                    ):
                        content.append(text)

                # Multiple pages
                else:

                    if page == current_page and y > current_y:

                        content.append(text)

                    elif current_page < page < next_page:

                        content.append(text)

                    elif page == next_page and y < next_y:

                        content.append(text)

            sections.append({

                "title": heading["title"],

                "page": heading["page"],

                "content": " ".join(content)

            })

        return sections
