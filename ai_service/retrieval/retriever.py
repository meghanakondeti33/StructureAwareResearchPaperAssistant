"""
retriever.py

Structure-aware semantic retriever using BGE + FAISS.

Features:
- Dense semantic retrieval using BGE + FAISS
- Query normalization
- Section-aware intent detection
- Title relevance scoring
- Content relevance scoring
- Candidate reranking
- Direct section-title matching
- Relevance gate
- Duplicate removal

Author: Meghana
Project: Structure-Aware Research Paper Assistant
"""

import re

from ai_service.retrieval.embeddings import EmbeddingGenerator
from ai_service.retrieval.vector_store import VectorStore


class Retriever:

    def __init__(self):

        self.embedder = EmbeddingGenerator()
        self.vector_store = VectorStore()

    # =========================================================
    # Load Existing FAISS Index
    # =========================================================

    def load(self, index_path):

        self.vector_store.load_index(
            index_path
        )

    # =========================================================
    # Normalize Text
    # =========================================================

    @staticmethod
    def _normalize_text(text):

        if not text:
            return ""

        return re.sub(
            r"\s+",
            " ",
            str(text).lower()
        ).strip()

    # =========================================================
    # Query Terms
    # =========================================================

    @staticmethod
    def _query_terms(query):

        stop_words = {
            # Question words
            "what",
            "is",
            "are",
            "was",
            "were",
            "who",
            "when",
            "where",
            "which",

            # Articles / connectors
            "the",
            "a",
            "an",
            "of",
            "to",
            "in",
            "on",
            "for",
            "and",
            "or",
            "with",
            "from",
            "about",
            "into",
            "than",

            # Auxiliary / modal verbs
            "how",
            "why",
            "does",
            "do",
            "did",
            "can",
            "could",
            "would",
            "should",

            # Conversational words
            "this",
            "that",
            "these",
            "those",
            "explain",
            "describe",
            "tell",
            "me",
            "give",
            "show",
            "provide",
            "please",

            # Paper-query words
            "paper",
            "document",
            "article"
        }

        words = re.findall(
        r"\b[a-zA-Z0-9][a-zA-Z0-9_-]*\b",
        Retriever._normalize_text(query)
    )
        return {
            word
            for word in words
            if word not in stop_words
            and len(word) > 1
        }

    # =========================================================
    # Detect Section Intent
    # =========================================================

    @staticmethod
    def _section_intent(query):

        """
        Detect whether the user is explicitly asking about
        a known research-paper section.

        Examples:

        "give conclusion of this paper"
            -> conclusion

        "summarize the methodology"
            -> methodology

        "what are the results"
            -> results
        """

        query = Retriever._normalize_text(
            query
        )

        section_aliases = {

            "abstract": [
                "abstract",
                "summary"
            ],

            "introduction": [
                "introduction",
                "intro"
            ],

            "related work": [
                "related work",
                "related works",
                "literature review",
                "background"
            ],

            "methodology": [
                "methodology",
                "method",
                "methods",
                "approach"
            ],

            "experiments": [
                "experiments",
                "experiment",
                "experimental setup"
            ],

            "results": [
                "results",
                "result",
                "findings",
                "findings and results"
            ],

            "discussion": [
                "discussion"
            ],

            "conclusion": [
                "conclusion",
                "conclusions",
                "summary and conclusion",
                "final conclusion",
                "concluding remarks"
            ],

            "limitations": [
                "limitations",
                "limitations of the study",
                "limitations of the paper"
            ],

            "future work": [
                "future work",
                "future research",
                "future directions"
            ]
        }

        # Prefer longer phrases first
        for canonical_name, aliases in section_aliases.items():

            for alias in sorted(
                aliases,
                key=len,
                reverse=True
            ):

                if re.search(
                    r"\b"
                    + re.escape(alias)
                    + r"\b",
                    query
                ):
                    return canonical_name

        return None

    # =========================================================
    # Section Title Matching
    # =========================================================

    def _section_title_score(
        self,
        query,
        chunk
    ):

        intent = self._section_intent(
            query
        )

        if not intent:
            return 0.0

        title = self._normalize_text(
            chunk.get(
                "title",
                ""
            )
        )

        if not title:
            return 0.0

        # -----------------------------------------------------
        # Exact / near exact section matching
        # -----------------------------------------------------

        if intent == title:
            return 1.0

        section_aliases = {

            "abstract": [
                "abstract",
                "summary"
            ],

            "introduction": [
                "introduction",
                "intro"
            ],

            "related work": [
                "related work",
                "related works",
                "literature review",
                "background"
            ],

            "methodology": [
                "methodology",
                "method",
                "methods",
                "approach"
            ],

            "experiments": [
                "experiments",
                "experiment",
                "experimental setup"
            ],

            "results": [
                "results",
                "result",
                "findings"
            ],

            "discussion": [
                "discussion"
            ],

            "conclusion": [
                "conclusion",
                "conclusions",
                "summary and conclusion",
                "concluding remarks"
            ],

            "limitations": [
                "limitations"
            ],

            "future work": [
                "future work",
                "future research",
                "future directions"
            ]
        }

        aliases = section_aliases.get(
            intent,
            []
        )

        for alias in aliases:

            if (
                title == alias
                or alias in title
            ):
                return 1.0

        return 0.0

    # =========================================================
    # Title Relevance
    # =========================================================

    def _title_relevance(
        self,
        query,
        chunk
    ):

        # -----------------------------------------------------
        # Section-aware score gets priority
        # -----------------------------------------------------

        section_score = self._section_title_score(
            query,
            chunk
        )

        if section_score > 0:
            return section_score

        query_terms = self._query_terms(
            query
        )

        if not query_terms:
            return 0.0

        title = self._normalize_text(
            chunk.get(
                "title",
                ""
            )
        )

        if not title:
            return 0.0

        title_terms = set(
            re.findall(
                r"\b[a-zA-Z0-9][a-zA-Z0-9_-]*\b",
                title
            )
        )

        overlap = query_terms.intersection(
            title_terms
        )

        return (
            len(overlap)
            / len(query_terms)
        )

    # =========================================================
    # Content Relevance
    # =========================================================

    def _content_relevance(
        self,
        query,
        chunk
    ):

        query_terms = self._query_terms(
            query
        )

        if not query_terms:
            return 0.0

        content = self._normalize_text(
            chunk.get(
                "content",
                ""
            )
        )

        if not content:
            return 0.0

        matched = 0

        for term in query_terms:

            # Word boundary matching prevents
            # accidental partial-word matches.

            if re.search(
                r"\b"
                + re.escape(term)
                + r"\b",
                content
            ):
                matched += 1

        return (
            matched
            / len(query_terms)
        )

    # =========================================================
    # Add Direct Section Candidates
    # =========================================================

    def _add_section_candidates(
        self,
        query,
        chunks,
        results,
        query_embedding
    ):

        """
        FAISS may fail to return a section even when its title
        is an exact match.

        Example:

            Query:
            "give conclusion of this paper"

            Chunk title:
            "Conclusion"

        This method guarantees that explicitly requested
        sections are considered by the reranker.
        """

        intent = self._section_intent(
            query
        )

        if not intent:
            return results

        existing_keys = set()

        for result in results:

            chunk = result.get(
                "chunk",
                {}
            )

            key = (
                str(
                    chunk.get(
                        "title",
                        ""
                    )
                ).strip().lower(),

                chunk.get(
                    "page",
                    0
                ),

                str(
                    chunk.get(
                        "content",
                        ""
                    )
                )[:150].strip().lower()
            )

            existing_keys.add(
                key
            )

        # -----------------------------------------------------
        # Find matching sections in ALL chunks
        # -----------------------------------------------------

        for chunk in chunks:

            title_score = self._section_title_score(
                query,
                chunk
            )

            if title_score <= 0:
                continue

            key = (
                str(
                    chunk.get(
                        "title",
                        ""
                    )
                ).strip().lower(),

                chunk.get(
                    "page",
                    0
                ),

                str(
                    chunk.get(
                        "content",
                        ""
                    )
                )[:150].strip().lower()
            )

            if key in existing_keys:
                continue

            # -------------------------------------------------
            # Calculate semantic similarity between query and
            # section title.
            # -------------------------------------------------

            title = chunk.get(
                "title",
                ""
            )

            try:

                title_embedding = (
                    self.embedder.embed_text(
                        title
                    )
                )

                semantic_score = float(
                    query_embedding @ title_embedding
                )

            except Exception:

                semantic_score = 0.0

            results.append(
                {
                    "score": semantic_score,
                    "chunk": chunk
                }
            )

            existing_keys.add(
                key
            )

        return results

    # =========================================================
    # Rerank Results
    # =========================================================

    def _rerank(
        self,
        query,
        results
    ):

        for result in results:

            chunk = result["chunk"]

            semantic_score = float(
                result.get(
                    "score",
                    0.0
                )
            )

            title_score = (
                self._title_relevance(
                    query,
                    chunk
                )
            )

            content_score = (
                self._content_relevance(
                    query,
                    chunk
                )
            )

            section_score = (
                self._section_title_score(
                    query,
                    chunk
                )
            )

            # -------------------------------------------------
            # Standard ranking
            # -------------------------------------------------

            final_score = (
                0.70 * semantic_score
                + 0.15 * title_score
                + 0.10 * content_score
                + 0.05 * section_score
            )

            # -------------------------------------------------
            # Strong section intent
            # -------------------------------------------------

            # If the user explicitly asks for a section and
            # the chunk title matches that section, guarantee
            # that it ranks very highly.

            if section_score >= 1.0:

                final_score = max(
                    final_score,
                    0.85
                )

            result["semantic_score"] = (
                semantic_score
            )

            result["title_score"] = (
                title_score
            )

            result["content_score"] = (
                content_score
            )

            result["section_score"] = (
                section_score
            )

            result["final_score"] = (
                final_score
            )

        results.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )

        return results

    # =========================================================
    # Remove Duplicate Results
    # =========================================================

    @staticmethod
    def _remove_duplicates(
        results,
        max_results=5
    ):

        selected = []
        seen = set()

        for result in results:

            chunk = result["chunk"]

            title = str(
                chunk.get(
                    "title",
                    ""
                )
            ).strip().lower()

            page = chunk.get(
                "page",
                0
            )

            content = str(
                chunk.get(
                    "content",
                    ""
                )
            ).strip().lower()

            key = (
                title,
                page,
                content[:150]
            )

            if key in seen:
                continue

            seen.add(key)

            selected.append(
                result
            )

            if len(selected) >= max_results:
                break

        return selected

    # =========================================================
    # Relevance Gate
    # =========================================================

    def is_relevant(
        self,
        query,
        results,
        threshold=0.60
    ):

        """
        Determine whether the retrieved evidence is relevant.

        Rules:

        1. Strong semantic similarity -> relevant
        2. Explicit section-title match -> relevant
        3. Strong lexical content match -> relevant
        4. Otherwise -> reject
        """

        if not results:
            return False

        # -----------------------------------------------------
        # Best scores
        # -----------------------------------------------------

        best_semantic_score = max(
            float(
                result.get(
                    "semantic_score",
                    result.get(
                        "score",
                        0.0
                    )
                )
            )
            for result in results
        )

        best_content_score = max(
            float(
                result.get(
                    "content_score",
                    0.0
                )
            )
            for result in results
        )

        best_title_score = max(
            float(
                result.get(
                    "title_score",
                    0.0
                )
            )
            for result in results
        )

        best_section_score = max(
            float(
                result.get(
                    "section_score",
                    0.0
                )
            )
            for result in results
        )

        # -----------------------------------------------------
        # Rule 1:
        # Strong semantic similarity
        # -----------------------------------------------------

        if best_semantic_score >= threshold:
            return True

        # -----------------------------------------------------
        # Rule 2:
        # Explicit section match
        # -----------------------------------------------------

        if best_section_score >= 1.0:
            return True

        # -----------------------------------------------------
        # Rule 3:
        # Strong title match
        # -----------------------------------------------------

        if best_title_score >= 0.50:
            return True

        # -----------------------------------------------------
        # Rule 4:
        # Strong content overlap
        # -----------------------------------------------------

        if best_content_score >= 0.40:
            return True

        # -----------------------------------------------------
        # Otherwise reject
        # -----------------------------------------------------

        return False

    # =========================================================
    # Search
    # =========================================================

    def retrieve(
        self,
        query,
        chunks,
        top_k=5
    ):

        if not query or not query.strip():
            return [], False

        if not chunks:
            return [], False

        if self.vector_store.size() == 0:

            raise RuntimeError(
                "FAISS index is empty."
            )

        # -----------------------------------------------------
        # Embed User Query
        # -----------------------------------------------------

        query_embedding = (
            self.embedder.embed_text(
                query
            )
        )

        # -----------------------------------------------------
        # Retrieve More Candidates
        # -----------------------------------------------------

        candidate_k = min(
            max(
                top_k * 4,
                20
            ),
            len(chunks)
        )

        scores, indices = (
            self.vector_store.search(
                query_embedding,
                top_k=candidate_k
            )
        )

        results = []

        for score, idx in zip(
            scores,
            indices
        ):

            idx = int(idx)

            if idx < 0:
                continue

            if idx >= len(chunks):
                continue

            results.append(
                {
                    "score": float(score),
                    "chunk": chunks[idx]
                }
            )

        # -----------------------------------------------------
        # Add direct section candidates
        # -----------------------------------------------------

        results = self._add_section_candidates(
            query=query,
            chunks=chunks,
            results=results,
            query_embedding=query_embedding
        )

        # -----------------------------------------------------
        # Rerank
        # -----------------------------------------------------

        results = self._rerank(
            query,
            results
        )

        # -----------------------------------------------------
        # Remove Duplicates
        # -----------------------------------------------------

        results = self._remove_duplicates(
            results,
            max_results=top_k
        )

        # -----------------------------------------------------
        # Relevance Gate
        # -----------------------------------------------------

        relevant = self.is_relevant(
            query,
            results
        )

        # -----------------------------------------------------
        # Debug Information
        # -----------------------------------------------------

        if results:

            best = results[0]

            print(
                "\nRetrieval Debug:"
            )

            print(
                f"Query           : {query}"
            )

            print(
                f"Top Section     : "
                f"{best['chunk'].get('title', 'Unknown')}"
            )

            print(
                f"Semantic Score  : "
                f"{best.get('semantic_score', 0):.4f}"
            )

            print(
                f"Title Score     : "
                f"{best.get('title_score', 0):.4f}"
            )

            print(
                f"Content Score   : "
                f"{best.get('content_score', 0):.4f}"
            )

            print(
                f"Section Score   : "
                f"{best.get('section_score', 0):.4f}"
            )

            print(
                f"Final Score     : "
                f"{best.get('final_score', 0):.4f}"
            )

            print(
                f"Relevant        : "
                f"{relevant}"
            )

        return results, relevant