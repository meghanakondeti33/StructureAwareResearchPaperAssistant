"""
gemini_client.py

Gemini client for grounded answer generation.

The LLM generates a clean answer without inline citations.
Retrieved sources are displayed separately by the application UI.

Author: Meghana
Project: Structure-Aware Research Paper Assistant
"""

import os
from pathlib import Path

from dotenv import load_dotenv

try:
    from google import genai
except ImportError:
    genai = None


class GeminiClient:

    def __init__(self):
        """
        Initialize Gemini client.

        Environment variable:
            GEMINI_API_KEY
        """

        self.client = None
        self._last_key = None

        # -------------------------------------------------------
        # Load environment variables
        # -------------------------------------------------------

        load_dotenv(override=True)

        api_key = os.getenv("GEMINI_API_KEY")

        # -------------------------------------------------------
        # Fallback environment locations
        # -------------------------------------------------------

        if not api_key:

            current_file = Path(__file__).resolve()

            # ai_service/generation/gemini_client.py
            ai_service_dir = current_file.parent.parent

            # Project root
            project_root = ai_service_dir.parent

            possible_env_files = [
                ai_service_dir / ".env",
                project_root / ".env",
                project_root / "backend" / ".env",
            ]

            for env_file in possible_env_files:

                if env_file.exists():

                    load_dotenv(
                        dotenv_path=env_file,
                        override=True
                    )

                    api_key = os.getenv("GEMINI_API_KEY")

                    if api_key:
                        break

        # -------------------------------------------------------
        # Check API key
        # -------------------------------------------------------

        if not api_key:

            print(
                "\nWarning: GEMINI_API_KEY not found. "
                "Gemini generation will use fallback mode."
            )

            return

        # -------------------------------------------------------
        # Initialize Gemini
        # -------------------------------------------------------

        if genai is None:

            print(
                "\nWarning: google-genai package is not installed."
            )

            return

        try:

            self.client = genai.Client(
                api_key=api_key
            )

            self._last_key = api_key

            print(
                "\nGemini Client initialized successfully!"
            )

        except Exception as e:

            print(
                f"\nWarning: Could not initialize Gemini Client: {e}"
            )

            self.client = None

    # ===========================================================
    # Generate Answer
    # ===========================================================

    def generate_answer(
        self,
        question,
        retrieved_chunks
    ):
        """
        Generate a grounded answer using retrieved paper chunks.

        Important:
        The generated answer intentionally contains NO:
        - Source 1 / Source 2 references
        - Page numbers
        - Similarity scores
        - Retrieval metadata
        - Citation markers

        The UI displays retrieved sources separately.
        """

        # -------------------------------------------------------
        # Validate retrieved chunks
        # -------------------------------------------------------

        if not retrieved_chunks:

            return (
                "I could not find enough relevant information "
                "in the paper to answer this question."
            )

        # -------------------------------------------------------
        # Re-check API key
        # -------------------------------------------------------

        api_key = os.getenv("GEMINI_API_KEY")

        if api_key and (
            not self.client
            or self._last_key != api_key
        ):

            try:

                if genai is not None:

                    self.client = genai.Client(
                        api_key=api_key
                    )

                    self._last_key = api_key

            except Exception as e:

                print(
                    f"Gemini client initialization error: {e}"
                )

                self.client = None

        # -------------------------------------------------------
        # Fallback if Gemini is unavailable
        # -------------------------------------------------------

        if not self.client:

            return self._fallback_response(
                question,
                retrieved_chunks
            )

        # =======================================================
        # Build context
        # =======================================================

        context_parts = []

        for i, result in enumerate(retrieved_chunks):

            chunk = result.get("chunk", {})

            title = chunk.get(
                "title",
                "Section"
            )

            page = chunk.get(
                "page",
                0
            )

            content = chunk.get(
                "content",
                ""
            )

            if not content:
                continue

            context_parts.append(
                f"""
--- Retrieved Evidence {i + 1} ---

Section:
{title}

Page:
{page + 1}

Content:
{content}
"""
            )

        context = "\n".join(context_parts)

        # -------------------------------------------------------
        # No usable context
        # -------------------------------------------------------

        if not context.strip():

            return (
                "I could not find enough relevant information "
                "in the paper to answer this question."
            )

        # =======================================================
        # Grounded prompt
        # =======================================================

        prompt = f"""
You are a research paper question-answering assistant.

Your job is to answer the user's question using ONLY the
information contained in the retrieved evidence below.

=========================
RETRIEVED EVIDENCE
=========================

{context}

=========================
USER QUESTION
=========================

{question}

=========================
ANSWERING RULES
=========================

1. Answer ONLY from the retrieved evidence.

2. Do NOT use outside knowledge.

3. Do NOT invent or assume information.

4. If the retrieved evidence does not contain enough
   information to answer the question, respond exactly:

   I could not find the answer in the paper.

5. Give a clear, natural and concise answer.

6. Combine information from multiple retrieved sections
   when necessary.

7. Do NOT mention the retrieval process.

8. Do NOT mention "retrieved chunks", "context", or
   "evidence" in the final answer.

9. Do NOT include source numbers.

10. Do NOT include page numbers.

11. Do NOT include citations.

12. Do NOT write phrases such as:
    - Source 1
    - Source 2
    - Source 3
    - Page 2
    - Page 10
    - According to Source 1
    - Based on the retrieved context

13. The application UI already displays the retrieved
    sources separately, so the answer itself must remain
    clean and readable.

14. Answer directly without unnecessary introductory text.

=========================
FINAL ANSWER
=========================
"""

        # =======================================================
        # Gemini API call
        # =======================================================

        try:

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            answer = response.text

            if not answer or not answer.strip():

                return (
                    "I could not generate an answer from "
                    "the information available in the paper."
                )

            # ---------------------------------------------------
            # Clean accidental citation/source references
            # ---------------------------------------------------

            answer = self._clean_answer(answer)

            return answer.strip()

        except Exception as e:

            print(
                f"Gemini API Call Error: {str(e)}"
            )

            return self._fallback_response(
                question,
                retrieved_chunks,
                error=e
            )

    # ===========================================================
    # Clean Answer
    # ===========================================================

    def _clean_answer(self, answer):
        """
        Remove common source/citation phrases that Gemini may
        occasionally add despite the prompt.
        """

        if not answer:
            return answer

        lines = answer.splitlines()

        cleaned_lines = []

        for line in lines:

            stripped = line.strip()

            # Remove standalone source references
            if stripped.lower().startswith(
                ("source 1", "source 2", "source 3",
                 "source 4", "source 5")
            ):
                continue

            cleaned_lines.append(line)

        answer = "\n".join(cleaned_lines)

        return answer.strip()

    # ===========================================================
    # Fallback Response
    # ===========================================================

    def _fallback_response(
        self,
        question,
        retrieved_chunks,
        error=None
    ):
        """
        Fallback response when Gemini is unavailable.

        This intentionally provides only a short context preview.
        """

        snippets = []

        for result in retrieved_chunks[:3]:

            chunk = result.get(
                "chunk",
                {}
            )

            content = chunk.get(
                "content",
                ""
            )

            if not content:
                continue

            snippets.append(
                content[:350].strip()
                + "..."
            )

        if not snippets:

            return (
                "I could not find enough relevant information "
                "in the paper to answer this question."
            )

        # -------------------------------------------------------
        # Do not expose technical API errors to the user
        # -------------------------------------------------------

        return (
            "I found relevant information in the paper, "
            "but I could not generate the AI-synthesized "
            "answer right now. Please try again."
        )