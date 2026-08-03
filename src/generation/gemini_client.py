"""
gemini_client.py

Gemini client for answer generation.

Author: Meghana
Project: Structure-Aware Multimodal Research Paper Assistant
"""

import os

from dotenv import load_dotenv
from google import genai


class GeminiClient:

    def __init__(self):

        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in .env"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        print("\nGemini Ready!")

    # -------------------------------------------------------
    # Generate Answer
    # -------------------------------------------------------

    def generate_answer(
        self,
        question,
        retrieved_chunks
    ):

        context = ""

        for chunk in retrieved_chunks:

            context += f"""
Section: {chunk['chunk']['title']}
Page: {chunk['chunk']['page'] + 1}

{chunk['chunk']['content']}

--------------------------------------
"""

        prompt = f"""
You are a research paper assistant.

Answer ONLY using the context below.

If the answer is not present, say:

"I could not find the answer in the paper."

=========================
Context
=========================

{context}

=========================
Question
=========================

{question}

Give a detailed but concise answer.
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text