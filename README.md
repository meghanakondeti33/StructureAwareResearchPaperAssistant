# 📚 Structure-Aware Research Paper Assistant

> **An AI-powered full-stack RAG application that lets users upload research papers, ask natural-language questions, and receive grounded answers based on the content of the selected paper.**

![Project Status](https://img.shields.io/badge/Status-Working-success)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![Vite](https://img.shields.io/badge/Vite-Frontend-646CFF?logo=vite)
![Node.js](https://img.shields.io/badge/Node.js-Express-339933?logo=node.js)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-AI_Service-009688?logo=fastapi)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-47A248?logo=mongodb)
![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-orange)
![Gemini](https://img.shields.io/badge/Google_Gemini-LLM-4285F4)
![RAG](https://img.shields.io/badge/AI-RAG-purple)

---

## 🎥 Demo

> A short demo showing the complete workflow:
>
> **Login → Upload Research Paper → Process PDF → Ask Questions → Retrieve Relevant Sections → Generate Grounded Answer → Inspect Sources**

### Demo Video

<!-- Add your demo video/GIF here -->

![Demo](docs/demo.gif)

---

# 📌 Overview

Research papers can be lengthy, technical, and difficult to navigate. Important information may be distributed across sections such as:

- Abstract
- Introduction
- Methodology
- Experiments
- Results
- Discussion
- Conclusion

A traditional keyword-based search system may fail to understand the semantic relationship between a user's question and the content of the paper.

The **Structure-Aware Research Paper Assistant** addresses this problem using a Retrieval-Augmented Generation (RAG) pipeline that preserves document structure during processing.

Instead of simply splitting a PDF into arbitrary pieces, the system:

1. Parses the PDF
2. Detects headings and sections
3. Groups content according to document structure
4. Creates structure-aware chunks
5. Generates BGE embeddings
6. Stores embeddings in FAISS
7. Retrieves relevant chunks
8. Reranks retrieved candidates
9. Applies a relevance gate
10. Uses Google Gemini to generate a grounded answer
11. Displays the retrieved sources separately

---

# 🎯 Problem Statement

Reading and searching through research papers manually can be time-consuming.

Traditional approaches have several limitations:

- Keyword search may miss semantically related content.
- Naive chunking can separate text from its logical section.
- Vector retrieval may return the closest available chunk even when it does not answer the question.
- LLMs may generate unsupported answers when given insufficient context.
- Users may not know which part of the paper was used to generate an answer.

This project aims to build a more structured and transparent research-paper question-answering system.

---

# 💡 Proposed Solution

The system combines **document structure awareness**, **semantic retrieval**, and **grounded LLM generation**.

### High-Level Pipeline

```text
                 Research Paper PDF
                         │
                         ▼
                  PyMuPDF Parsing
                         │
                         ▼
                 Heading Detection
                         │
                         ▼
                  Section Detection
                         │
                         ▼
              Structure-Aware Chunking
                         │
                         ▼
                  BGE Embeddings
                         │
                         ▼
                    FAISS Index
                         │
                         ▼
                   User Question
                         │
                         ▼
                  Query Embedding
                         │
                         ▼
                 FAISS Retrieval
                         │
                         ▼
                     Reranking
                         │
                         ▼
                  Relevance Gate
                     /       \
                    /         \
              Relevant       Irrelevant
                 │               │
                 ▼               ▼
              Gemini         Reject
                 │
                 ▼
          Grounded Answer
                 │
                 ▼
        Retrieved Sources
```

---

# ✨ Key Features

## 🔐 1. User Authentication

The application provides:

- User registration
- User login
- Password hashing using bcrypt
- JWT-based authentication
- Protected API routes

Authentication is handled by the Node.js backend.

---

## 📄 2. Research Paper Upload

Users can upload PDF research papers through the dashboard.

The uploaded document is:

```text
React
  ↓
Node.js / Express
  ↓
FastAPI AI Service
```

The backend stores document information in MongoDB and sends the PDF to the AI service for processing.

---

## 🧠 3. Structure-Aware PDF Processing

The system uses **PyMuPDF** to extract PDF text and layout information.

The processing pipeline considers information such as:

- Text blocks
- Font information
- Font size
- Bounding boxes
- Page numbers
- Document layout

This information is used to identify potential section headings.

---

## 🏷️ 4. Heading and Section Detection

The system attempts to identify logical sections within the research paper.

For example:

```text
Research Paper
│
├── Abstract
├── Introduction
├── Related Work
├── Methodology
├── Experiments
├── Results
├── Discussion
└── Conclusion
```

The detected section information is retained as metadata throughout the retrieval pipeline.

---

## ✂️ 5. Structure-Aware Chunking

Instead of treating the entire PDF as a single text block, the application divides the paper into smaller retrieval-friendly chunks.

Each chunk preserves metadata such as:

```json
{
  "title": "Transformer",
  "page": 2,
  "content": "The Transformer is..."
}
```

This allows retrieved information to remain associated with its section and page.

---

# 🔢 6. Semantic Embeddings with BGE

The project uses:

```text
BAAI/bge-small-en-v1.5
```

through Sentence Transformers.

Document chunks are converted into dense vector representations.

A user question is also converted into a vector:

```text
"What is self-attention?"
          │
          ▼
       BGE Model
          │
          ▼
   384-dimensional vector
```

The question vector can then be compared against document vectors.

---

# ⚡ 7. FAISS Vector Search

The project uses **FAISS** for efficient vector similarity search.

The current vector store uses:

```text
FAISS IndexFlatIP
```

with normalized embeddings.

The indexing workflow is:

```text
Document Chunks
      ↓
BGE Embeddings
      ↓
FAISS
      ↓
Document-specific Vector Index
```

Each processed document can have its own vector index and metadata file.

---

# 🎯 8. Retrieval and Reranking

The system does not rely only on the initial FAISS ranking.

Retrieved candidates are further evaluated using information such as:

- Semantic similarity
- Section title relevance
- Content relevance
- Section intent

This improves retrieval for queries that explicitly refer to sections.

For example:

```text
User:
"Give the conclusion of this paper."

        ↓

Detected intent:
"conclusion"

        ↓

Candidate:
Section = "Conclusion"

        ↓

Strong section match
```

This allows section-oriented questions to be handled more reliably.

---

# 🛡️ 9. Relevance Gate

One of the important features of the system is the **relevance gate**.

A vector database will always return the nearest available vectors, even if the paper does not contain the answer.

For example:

```text
Question:

"What is the population of India?"
```

If the uploaded paper is about Transformers and contains no information about India's population, the system should not ask the LLM to invent an answer.

Instead:

```text
I could not find the answer in the paper.
```

### Relevance Flow

```text
User Question
      ↓
Semantic Retrieval
      ↓
Reranking
      ↓
Relevance Check
      │
      ├── Relevant ──────► Gemini
      │                       ↓
      │                  Grounded Answer
      │
      └── Not Relevant ──► Reject
```

This provides an additional layer of protection against unsupported answers.

---

# 🤖 10. Grounded Gemini Answer Generation

When relevant evidence is found, the retrieved document content is passed to Google Gemini.

The model is instructed to:

- Use only the provided paper content
- Avoid external knowledge
- Avoid guessing
- Avoid inventing information
- Answer clearly and concisely
- State when the answer cannot be found

The final answer is intentionally kept clean.

For example:

```text
The Transformer is a sequence-to-sequence model
based entirely on attention. It replaces recurrent
layers with multi-headed self-attention and uses
stacked self-attention and point-wise fully connected
layers in both the encoder and decoder.
```

The source information is displayed separately in the UI.

---

# 📚 11. Retrieved Source Transparency

The application allows users to inspect the evidence retrieved for an answer.

Users can expand:

```text
▸ View Retrieved Sources (5)
```

and see:

- Section title
- Page number
- Retrieved text snippet
- Similarity / match score

Example:

```text
SOURCE

📌 Transformer
Page 2
64.8% Match

"The Transformer is the first sequence
transduction model based entirely on attention..."
```

This makes the RAG pipeline more transparent.

---

# 🖥️ Application Workflow

## Step 1 — Register

The user creates an account.

```text
Register
   ↓
MongoDB
   ↓
JWT Authentication
```

---

## Step 2 — Login

The user logs into the application.

```text
Login
  ↓
Express Backend
  ↓
bcrypt Password Verification
  ↓
JWT Token
  ↓
Dashboard
```

---

## Step 3 — Upload a Research Paper

The user uploads a PDF from the dashboard.

```text
React Dashboard
      ↓
Express API
      ↓
Multer File Upload
      ↓
MongoDB Document Record
      ↓
FastAPI AI Service
```

---

## Step 4 — Process the PDF

The AI service performs:

```text
PDF
 ↓
PyMuPDF
 ↓
Heading Detection
 ↓
Section Detection
 ↓
Metadata Construction
 ↓
Structure-Aware Chunking
 ↓
BGE Embeddings
 ↓
FAISS Index
```

---

## Step 5 — Ask a Question

The user opens the chat page and asks a question.

Example:

```text
What is the architecture of the Transformer?
```

---

## Step 6 — Retrieve Relevant Context

The query goes through:

```text
Question
   ↓
BGE Query Embedding
   ↓
FAISS Search
   ↓
Candidate Retrieval
   ↓
Reranking
   ↓
Relevance Gate
```

---

## Step 7 — Generate Answer

If sufficient relevant information is found:

```text
Relevant Context
       ↓
Gemini
       ↓
Grounded Answer
```

---

## Step 8 — Inspect Sources

The user can expand the retrieved sources to understand which sections of the paper contributed to the answer.

---

# 🏗️ System Architecture

```text
                         USER
                           │
                           ▼
                ┌─────────────────────┐
                │    React + Vite     │
                │      Frontend       │
                └──────────┬──────────┘
                           │
                     REST / HTTP
                           │
                           ▼
                ┌─────────────────────┐
                │   Node.js + Express │
                │    API Gateway      │
                └───────┬───────┬─────┘
                        │       │
                        │       │
                        ▼       ▼
                 ┌──────────┐  ┌──────────────────┐
                 │ MongoDB  │  │  FastAPI AI      │
                 │          │  │    Service       │
                 └──────────┘  └────────┬─────────┘
                                        │
                                        ▼
                                ┌───────────────┐
                                │    PyMuPDF    │
                                │ PDF Processing │
                                └───────┬───────┘
                                        │
                                        ▼
                                ┌───────────────┐
                                │    Heading    │
                                │   Detection   │
                                └───────┬───────┘
                                        │
                                        ▼
                                ┌───────────────┐
                                │    Section    │
                                │   Detection   │
                                └───────┬───────┘
                                        │
                                        ▼
                                ┌───────────────┐
                                │  Structure-   │
                                │ Aware Chunking │
                                └───────┬───────┘
                                        │
                                        ▼
                                ┌───────────────┐
                                │ BGE Embeddings│
                                └───────┬───────┘
                                        │
                                        ▼
                                ┌───────────────┐
                                │     FAISS     │
                                │ Vector Search │
                                └───────┬───────┘
                                        │
                                        ▼
                                ┌───────────────┐
                                │   Reranking   │
                                └───────┬───────┘
                                        │
                                        ▼
                                ┌───────────────┐
                                │ Relevance Gate│
                                └───────┬───────┘
                                        │
                                        ▼
                                ┌───────────────┐
                                │ Google Gemini │
                                │      LLM      │
                                └───────┬───────┘
                                        │
                                        ▼
                                ┌───────────────┐
                                │ Answer +      │
                                │ Sources       │
                                └───────────────┘
```

---

# 🔄 End-to-End Data Flow

## Document Ingestion

```text
PDF Upload
    ↓
React
    ↓
POST /api/upload
    ↓
Express + Multer
    ↓
MongoDB Document Record
    ↓
POST /process-pdf
    ↓
FastAPI
    ↓
PyMuPDF
    ↓
Section Detection
    ↓
Chunking
    ↓
BGE
    ↓
FAISS
    ↓
Document Ready
```

---

## Question Answering

```text
User Question
      ↓
React
      ↓
POST /api/ask
      ↓
Express
      ↓
POST /query
      ↓
FastAPI
      ↓
Load Document FAISS Index
      ↓
BGE Query Embedding
      ↓
FAISS Search
      ↓
Reranking
      ↓
Relevance Gate
      │
      ├──────────── Relevant
      │                 ↓
      │              Gemini
      │                 ↓
      │          Grounded Answer
      │
      └──────────── Not Relevant
                        ↓
                "I could not find
                 the answer in
                 the paper."
```

---

# 🧪 Example Queries

The application can be tested with questions such as:

### Definition

```text
What is the Transformer?
```

### Architecture

```text
What is the architecture of the Transformer?
```

### Specific Fact

```text
How many encoder and decoder stacks are used?
```

### Concept

```text
What is self-attention?
```

### Section Query

```text
What is the conclusion of this paper?
```

### Summary Query

```text
Summarize the methodology used in the paper.
```

### Out-of-Scope Query

```text
What is the population of India?
```

Expected behavior when the paper does not contain the answer:

```text
I could not find the answer in the paper.
```

---

# 🛠️ Technology Stack

## Frontend

| Technology | Purpose |
|---|---|
| React | User interface |
| Vite | Frontend development and build tooling |
| Tailwind CSS | UI styling |
| Axios | API communication |
| React Router | Client-side navigation |

---

## Backend

| Technology | Purpose |
|---|---|
| Node.js | Backend runtime |
| Express.js | REST API server |
| MongoDB | Application database |
| Mongoose | MongoDB ODM |
| JWT | Authentication |
| bcrypt | Password hashing |
| Multer | PDF/file upload handling |

---

## AI Service

| Technology | Purpose |
|---|---|
| Python | AI pipeline |
| FastAPI | AI microservice API |
| PyMuPDF | PDF parsing and layout extraction |
| Sentence Transformers | Text embeddings |
| BAAI/bge-small-en-v1.5 | Embedding model |
| FAISS | Vector similarity search |
| NumPy | Numerical operations |
| Google Gemini | Answer generation |

---

# 🧠 AI / ML Concepts

This project demonstrates practical implementation of:

- Retrieval-Augmented Generation (RAG)
- Natural Language Processing
- Dense embeddings
- Semantic search
- Vector similarity search
- Structure-aware chunking
- Document section detection
- Query intent detection
- Retrieval reranking
- Relevance filtering
- Prompt engineering
- Grounded LLM generation
- Hallucination mitigation

---

# 📁 Project Structure

```text
StructureAwareResearchPaperAssistant/
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   └── Chat.jsx
│   │   │
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── authApi.js
│   │   │   ├── chatApi.js
│   │   │   └── documentApi.js
│   │   │
│   │   └── ...
│   │
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── ...
│
├── backend/
│   ├── config/
│   │   └── db.js
│   │
│   ├── controllers/
│   │   ├── authController.js
│   │   ├── chatController.js
│   │   └── documentController.js
│   │
│   ├── middleware/
│   │   ├── authMiddleware.js
│   │   └── uploadMiddleware.js
│   │
│   ├── models/
│   │   ├── User.js
│   │   ├── Document.js
│   │   ├── Chat.js
│   │   └── Conversation.js
│   │
│   ├── routes/
│   │   ├── authRoutes.js
│   │   ├── chatRoutes.js
│   │   └── documentRoutes.js
│   │
│   ├── app.js
│   ├── server.js
│   ├── package.json
│   └── package-lock.json
│
├── ai_service/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── parser.py
│   │   ├── heading_scorer.py
│   │   ├── metadata_builder.py
│   │   └── section_detector.py
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── chunker.py
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   └── vector_store.py
│   │
│   ├── generation/
│   │   ├── __init__.py
│   │   └── gemini_client.py
│   │
│   ├── vector_stores/
│   │   └── .gitkeep
│   │
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
│
├── docs/
│   ├── demo.gif
│   └── screenshots/
│       ├── login.png
│       ├── dashboard.png
│       ├── upload.png
│       ├── chat.png
│       ├── retrieved-sources.png
│       └── relevance-gate.png
│
├── README.md
├── TECHNICAL_DOCUMENTATION.md
└── .gitignore
```

---

# ⚙️ Installation & Setup

## Prerequisites

Install the following:

- Python 3.10+
- Node.js 18+
- npm
- MongoDB
- Git

---

# 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/StructureAwareResearchPaperAssistant.git

cd StructureAwareResearchPaperAssistant
```

---

# 2. Configure MongoDB

Make sure MongoDB is running locally or provide a MongoDB connection string.

Example:

```text
mongodb://localhost:27017/research_knowledge_assistant
```

---

# 3. Setup the Backend

Open a terminal:

```powershell
cd backend
```

Install dependencies:

```powershell
npm install
```

Create:

```text
backend/.env
```

Add:

```env
PORT=5001
MONGO_URI=your_mongodb_connection_string
JWT_SECRET=your_jwt_secret
AI_SERVICE_URL=http://localhost:8001
```

---

# 4. Setup the AI Service

Open another terminal:

```powershell
cd ai_service
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

# 5. Configure Gemini

Create:

```text
ai_service/.env
```

Add:

```env
GEMINI_API_KEY=your_gemini_api_key
```

> Never commit your real API key to GitHub.

---

# 6. Start the AI Service

From the `ai_service` directory:

```powershell
python -m uvicorn main:app --reload --port 8001
```

The AI service will be available at:

```text
http://localhost:8001
```

FastAPI documentation:

```text
http://localhost:8001/docs
```

---

# 7. Start the Node.js Backend

Open another terminal:

```powershell
cd backend
```

Run:

```powershell
npm run dev
```

The backend runs on:

```text
http://localhost:5001
```

---

# 8. Start the Frontend

Open another terminal:

```powershell
cd frontend
```

Install dependencies if needed:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

Open the URL displayed by Vite.

Example:

```text
http://localhost:3000
```

---

# 🔐 Environment Variables

## Backend

```env
PORT=5001
MONGO_URI=your_mongodb_connection_string
JWT_SECRET=your_jwt_secret
AI_SERVICE_URL=http://localhost:8001
```

## AI Service

```env
GEMINI_API_KEY=your_gemini_api_key
```

### Never commit

```text
.env
```

or any file containing:

```text
API keys
JWT secrets
Database credentials
```

---

# 🚀 Running the Application

Three services need to run simultaneously.

### Terminal 1 — AI Service

```powershell
cd ai_service
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --port 8001
```

### Terminal 2 — Backend

```powershell
cd backend
npm run dev
```

### Terminal 3 — Frontend

```powershell
cd frontend
npm run dev
```

Then open the frontend URL shown by Vite.

---

# 🔌 API Architecture

## Authentication

```text
POST /api/register
POST /api/login
```

---

## Documents

```text
POST /api/upload
GET  /api/documents
```

---

## Chat

```text
POST /api/ask
GET  /api/history
```

---

## AI Service

```text
POST /process-pdf
POST /query
```

---

# 🧪 Testing Checklist

After starting all three services, verify:

### Authentication

- [ ] Register a new user
- [ ] Login successfully
- [ ] JWT authentication works
- [ ] Protected routes reject unauthorized requests

### Document Processing

- [ ] Upload a PDF
- [ ] Document status changes to processing
- [ ] FastAPI receives the PDF
- [ ] PDF parsing succeeds
- [ ] Sections are detected
- [ ] Chunks are created
- [ ] BGE embeddings are generated
- [ ] FAISS index is created
- [ ] Document becomes ready

### Question Answering

- [ ] Ask a relevant question
- [ ] Relevant chunks are retrieved
- [ ] Reranking works
- [ ] Relevance gate allows relevant questions
- [ ] Gemini generates an answer
- [ ] Sources are displayed separately

### Relevance Testing

Ask:

```text
What is the population of India?
```

when the paper is unrelated.

Expected:

```text
I could not find the answer in the paper.
```

---

# 📸 Screenshots

## 🔐 Login

![Login](docs/screenshots/login.png)

---

## 📊 Dashboard

![Dashboard](docs/screenshots/dashboard.png)

---

## 📄 Upload Research Paper

![Upload](docs/screenshots/upload.png)

---

## 💬 Research Paper Q&A

![Chat](docs/screenshots/chat.png)

---

## 📚 Retrieved Sources

![Retrieved Sources](docs/screenshots/retrieved-sources.png)

---

## 🛡️ Relevance Gate

![Relevance Gate](docs/screenshots/relevance-gate.png)

---

# 🎥 Recommended Demo

For a recruiter-facing demonstration, use the following sequence:

```text
1. Open Application
       ↓
2. Register / Login
       ↓
3. Open Dashboard
       ↓
4. Upload attention.pdf
       ↓
5. Show document processing
       ↓
6. Open Chat
       ↓
7. Ask:
   "What is the Transformer?"
       ↓
8. Show clean grounded answer
       ↓
9. Open:
   "View Retrieved Sources"
       ↓
10. Show section + page + match score
       ↓
11. Ask:
   "How many encoder and decoder stacks are used?"
       ↓
12. Show:
   N = 6 encoder stacks
   N = 6 decoder stacks
       ↓
13. Ask:
   "What is the conclusion of this paper?"
       ↓
14. Show conclusion-based answer
       ↓
15. Ask:
   "What is the population of India?"
       ↓
16. Show:
   "I could not find the answer in the paper."
```

This demonstrates both:

```text
Successful Retrieval
```

and:

```text
Out-of-Context Protection
```

---

# 🧠 Why Structure-Aware RAG?

A basic RAG system may perform:

```text
PDF
 ↓
Text Extraction
 ↓
Fixed-Size Chunking
 ↓
Embeddings
 ↓
Vector Search
 ↓
LLM
```

This project adds document structure:

```text
PDF
 ↓
Layout-Aware Parsing
 ↓
Heading Detection
 ↓
Section Detection
 ↓
Structure-Aware Chunking
 ↓
BGE Embeddings
 ↓
FAISS Retrieval
 ↓
Reranking
 ↓
Relevance Gate
 ↓
Gemini
 ↓
Grounded Answer
```

This is particularly useful for structured documents such as research papers where section context matters.

---

# 🛡️ Hallucination Mitigation Strategy

The project uses several layers to reduce unsupported answers.

### 1. Document Retrieval

The model receives relevant paper content rather than relying only on its general knowledge.

### 2. Structure-Aware Retrieval

Retrieved chunks retain their section and page metadata.

### 3. Reranking

Retrieved candidates are further evaluated before generation.

### 4. Relevance Gate

Clearly unsupported questions can be rejected.

### 5. Grounded Prompting

Gemini is instructed to answer using only the supplied paper content.

### 6. Source Transparency

Retrieved sections can be inspected separately by the user.

---

# ⚠️ Current Limitations

The current system has several limitations.

### PDF Formatting

Heading detection depends on document formatting and layout. Unusual PDF structures may reduce section-detection accuracy.

### Scanned PDFs

Scanned PDFs containing images rather than selectable text require OCR support.

### Figures and Tables

The current implementation does not deeply understand visual figures, charts, or tables.

### Ambiguous Questions

Highly ambiguous or multi-hop questions may still challenge retrieval.

### Chunking

The chunk size affects the balance between context completeness and retrieval noise.

### Single-Document Focus

The current workflow primarily focuses on querying a selected research paper rather than performing cross-paper retrieval.

### LLM Availability

Answer generation depends on the availability and rate limits of the Gemini API.

---

# 🚀 Future Improvements

## 🔹 Hybrid Retrieval

Combine:

```text
BM25 Keyword Search
        +
Dense Vector Search
```

to improve both lexical and semantic retrieval.

---

## 🔹 Cross-Encoder Reranking

Introduce a dedicated cross-encoder model to improve candidate relevance ranking.

---

## 🔹 Adaptive Chunking

Dynamically determine chunk boundaries based on:

- Section structure
- Paragraph boundaries
- Semantic coherence
- Document length

---

## 🔹 Hierarchical Retrieval

Use the paper's section hierarchy during retrieval:

```text
Paper
 ↓
Section
 ↓
Subsection
 ↓
Relevant Chunk
```

---

## 🔹 OCR Support

Add OCR for scanned research papers.

---

## 🔹 Multimodal Paper Understanding

Extend the system to understand:

- Figures
- Tables
- Charts
- Diagrams
- Figure captions

using vision-language models.

---

## 🔹 Multi-Document RAG

Allow users to upload multiple research papers and ask questions across them.

Example:

```text
Compare the methodologies used in these two papers.
```

---

## 🔹 Improved Citations

Provide more precise evidence such as:

```text
Paper
 ↓
Section
 ↓
Page
 ↓
Paragraph
```

---

## 🔹 RAG Evaluation

Introduce systematic evaluation using metrics such as:

- Retrieval Precision
- Retrieval Recall
- Context Relevance
- Answer Relevance
- Faithfulness

---

## 🔹 Conversation Memory

Allow users to maintain longer research conversations while preserving document grounding.

---

# 💼 Interview Explanation

### "Tell me about your project."

> I built a full-stack Structure-Aware Research Paper Assistant using React, Node.js, FastAPI, MongoDB, FAISS, BGE embeddings, and Google Gemini. The system allows users to upload research papers and ask natural-language questions about them. Instead of blindly splitting the PDF into fixed-size chunks, I first parse the document layout and detect logical sections such as Introduction, Methodology, Results, and Conclusion. The content is then converted into BGE embeddings and stored in FAISS for semantic retrieval. I added reranking and a relevance gate to improve retrieval quality and prevent unsupported questions from being passed to the LLM. Finally, Gemini generates a grounded answer using the retrieved paper content, while the UI displays the retrieved sections and page information separately.

---

# 🧩 Key Engineering Concepts Demonstrated

## Full-Stack Development

- React
- REST APIs
- Node.js
- Express.js
- MongoDB
- Authentication
- JWT
- File uploads
- Microservice communication

## AI / ML

- NLP
- Dense embeddings
- Semantic search
- Vector databases
- Information retrieval
- Document chunking
- Reranking
- Relevance filtering

## Generative AI

- RAG
- Prompt engineering
- Grounded generation
- LLM integration
- Hallucination mitigation

## System Design

- Three-tier architecture
- Python AI microservice
- API gateway
- Document ingestion pipeline
- Vector indexing
- Query pipeline
- Source transparency

---

# 🌟 Project Highlights

- 📄 Research paper PDF upload
- 🔐 JWT-based authentication
- 🧠 Structure-aware document processing
- 🏷️ Heading and section detection
- ✂️ Structure-aware chunking
- 🔢 BGE embeddings
- ⚡ FAISS vector search
- 🎯 Candidate reranking
- 🛡️ Relevance gate
- 🤖 Gemini-powered grounded answers
- 📚 Retrieved source transparency
- 💾 MongoDB persistence
- 🌐 React + Node.js + FastAPI architecture
- 🔌 Dedicated Python AI microservice

---

# 📊 Architecture at a Glance

```text
                    STRUCTURE-AWARE RAG
                           │
            ┌──────────────┴──────────────┐
            │                             │
       INDEXING PHASE                QUERY PHASE
            │                             │
            ▼                             ▼
        PDF Upload                  User Question
            │                             │
            ▼                             ▼
       PyMuPDF Parse                BGE Embedding
            │                             │
            ▼                             ▼
    Section Detection              FAISS Search
            │                             │
            ▼                             ▼
    Structure-Aware                  Reranking
       Chunking                          │
            │                            ▼
            ▼                     Relevance Gate
      BGE Embeddings                    │
            │                     ┌──────┴──────┐
            ▼                     │             │
          FAISS                 Relevant    Not Relevant
                                      │             │
                                      ▼             ▼
                                   Gemini        Reject
                                      │
                                      ▼
                              Grounded Answer
                                      │
                                      ▼
                              Retrieved Sources
```

---

# 👩‍💻 Authors

### Meghana Sri Kondeti

B.Tech — Computer Science & Engineering

Interests:

- Artificial Intelligence
- Machine Learning
- Generative AI
- Natural Language Processing
- Retrieval-Augmented Generation
- Computer Vision
- Full-Stack Development

### Surya Tej Meka

Project Contributor

---

# 📫 Connect

- **GitHub:** `YOUR_GITHUB_PROFILE`
- **LinkedIn:** `YOUR_LINKEDIN_PROFILE`
- **Email:** `YOUR_EMAIL`

---

# 📄 License

This project is developed for educational, research, and portfolio purposes.

If you intend to distribute or reuse the project, add an appropriate open-source license.

---

# ⭐ Final Note

The project demonstrates how traditional document processing, semantic retrieval, vector databases, LLMs, and full-stack engineering can be combined to build a practical AI application.

> **From PDF structure → semantic retrieval → relevance filtering → grounded generation.**

---