"""
gemini_client.py

Gemini client for answer generation with graceful fallback support.

Author: Meghana
Project: Structure-Aware Multimodal Research Paper Assistant
"""

import os
from pathlib import Path
from dotenv import load_dotenv

try:
    from google import genai
except ImportError:
    import google.generativeai as genai


class GeminiClient:

    def __init__(self):
        # Force load_dotenv with override=True so new keys in .env take effect immediately
        load_dotenv(override=True)

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            root_env = Path(__file__).resolve().parent.parent.parent / ".env"
            backend_env = Path(__file__).resolve().parent.parent.parent / "backend" / ".env"
            ai_env = Path(__file__).resolve().parent.parent / ".env"
            if ai_env.exists():
                load_dotenv(dotenv_path=ai_env, override=True)
            elif backend_env.exists():
                load_dotenv(dotenv_path=backend_env, override=True)
            elif root_env.exists():
                load_dotenv(dotenv_path=root_env, override=True)

            api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            self.client = None
            print("\nWarning: GEMINI_API_KEY not found in .env. Falling back to retrieved context preview.")
        else:
            try:
                self.client = genai.Client(api_key=api_key)
                print(f"\nGemini Client initialized successfully!")
            except Exception as e:
                print(f"\nWarning: Could not initialize Gemini Client: {str(e)}")
                self.client = None

    # -------------------------------------------------------
    # Generate Answer
    # -------------------------------------------------------

    def generate_answer(
        self,
        question,
        retrieved_chunks
    ):
        # Re-verify client and API key dynamically
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and (not self.client or getattr(self, '_last_key', None) != api_key):
            try:
                self.client = genai.Client(api_key=api_key)
                self._last_key = api_key
            except Exception as e:
                print(f"Client init error: {str(e)}")

        if not self.client:
            top_snippets = "\n\n".join([
                f"• [{chunk['chunk'].get('title', 'Section')}, Page {chunk['chunk'].get('page', 0) + 1}]:\n{chunk['chunk'].get('content', '')[:350]}..."
                for chunk in retrieved_chunks[:3]
            ])
            return f"Relevant context sections retrieved for '{question}':\n\n{top_snippets}\n\n(To generate AI synthesized answers, please add your GEMINI_API_KEY to .env)."

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

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini API Call Error: {str(e)}")
            top_snippets = "\n\n".join([
                f"• [{chunk['chunk'].get('title', 'Section')}, Page {chunk['chunk'].get('page', 0) + 1}]:\n{chunk['chunk'].get('content', '')[:350]}..."
                for chunk in retrieved_chunks[:3]
            ])
            return f"Retrieved Context Sections for '{question}':\n\n{top_snippets}\n\n(Error contacting Gemini API: {str(e)})"
