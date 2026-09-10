# Structure-Aware Research Paper Assistant

An intelligent research paper question-answering system that uses **Structure-Aware Retrieval-Augmented Generation (RAG)** to answer natural-language questions from research papers.

Unlike conventional PDF search, the system considers the **logical structure of academic papers** such as sections, headings, page numbers, and semantic relationships while creating the searchable knowledge base.

---

## Overview

Research papers are often long, dense, and difficult to navigate. Traditional PDF search mainly depends on exact keyword matching, which can fail when the user's question and the paper use different words to express the same idea.

For example:

> "What approach did the authors use to improve model performance?"

The relevant section may not contain those exact words.

This project addresses the problem using **semantic retrieval** combined with **document structure awareness**.

The system:

1. Parses the uploaded research paper.
2. Detects its structural sections and headings.
3. Creates structure-aware chunks.
4. Converts chunks into semantic embeddings.
5. Stores embeddings in a FAISS index.
6. Retrieves the most relevant sections for a user query.
7. Sends the retrieved context to Gemini.
8. Generates a concise, context-grounded answer with source information.

---

## Key Features

- 📄 Upload research papers in PDF format
- 🔍 Structure-aware PDF parsing
- 🧩 Section-based semantic chunking
- 🧠 Sentence Transformer embeddings
- ⚡ Fast semantic retrieval using FAISS
- 🤖 Gemini-powered answer generation
- 📑 Source-aware responses with section and page information
- 💬 Natural-language question answering
- 🖥️ Interactive Streamlit interface
- 🔒 API key managed through environment variables

---

# System Architecture

```text
                 Research Paper PDF
                         │
                         ▼
                  ┌─────────────┐
                  │  PyMuPDF    │
                  │   Parser    │
                  └──────┬──────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Section Detection│
                │ & Heading Scoring│
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Metadata Builder │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Structure-Aware  │
                │     Chunking     │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Sentence         │
                │ Transformer      │
                │    Embeddings    │
                └────────┬─────────┘
                         │
                         ▼
                    ┌─────────┐
                    │  FAISS  │
                    │  Index  │
                    └────┬────┘
                         │
                  User Question
                         │
                         ▼
                ┌──────────────────┐
                │ Semantic         │
                │ Retrieval        │
                └────────┬─────────┘
                         │
                    Top-K Chunks
                         │
                         ▼
                ┌──────────────────┐
                │ Google Gemini    │
                │ Answer Generation│
                └────────┬─────────┘
                         │
                         ▼
                  Grounded Answer
