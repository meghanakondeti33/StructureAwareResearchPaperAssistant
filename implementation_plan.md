# Implementation Plan: ResearchKnowledgeAssistant (Simplified Student Portfolio V2)

This document outlines the simplified, student-portfolio-focused full-stack architecture, folder structure, API design, database schemas, and implementation roadmap for **ResearchKnowledgeAssistant**.

The architecture preserves the professional **3-layer separation** while stripping away enterprise complexity (Docker, SSE, GridFS, background queues, complex sub-trees) to ensure a single developer can complete the project within 1–2 weeks.

---

## 1. System Architecture Overview

```mermaid
flowchart TB
    subgraph Client ["Frontend Layer (React SPA)"]
        Pages["Pages (Login, Register, Dashboard, Chat)"]
        Services["API Services (axios)"]
        Pages --> Services
    end

    subgraph Backend ["Backend Gateway (Node.js + Express)"]
        AuthMiddleware["JWT Auth Middleware"]
        Controllers["Controllers (Auth, Document, Chat)"]
        UploadMiddleware["Multer Storage (backend/uploads)"]
        
        Services -->|HTTP / REST| Controllers
        Controllers --> AuthMiddleware
        Controllers --> UploadMiddleware
    end

    subgraph Database ["Database Layer (MongoDB)"]
        MongoDb[(MongoDB: Users, Documents, Chats)]
        Controllers -->|Mongoose| MongoDb
    end

    subgraph AIService ["AI Service Layer (Python FastAPI)"]
        FastAPI["FastAPI App (main.py)"]
        
        subgraph CoreAI ["Core AI Pipeline"]
            Parser["parser.py"]
            Scorer["heading_scorer.py"]
            Detector["section_detector.py"]
            Metadata["metadata_builder.py"]
        end

        subgraph RetrievalAI ["Retrieval Engine"]
            Chunker["chunker.py"]
            Embeddings["embeddings.py"]
            FAISSStore["vector_store.py"]
            Retriever["retriever.py"]
        end

        subgraph GenAI ["LLM Generation"]
            Gemini["gemini_client.py"]
        end

        Controllers -->|HTTP REST Client| FastAPI
        FastAPI --> CoreAI
        FastAPI --> RetrievalAI
        FastAPI --> GenAI
    end

    subgraph VectorDisk ["Vector Storage"]
        FAISSFiles["FAISS Index Files (ai_service/vector_stores/)"]
        FAISSStore -->|Read/Write Index| VectorDisk
    end
```

---

## 2. Simplified Folder Structure

```text
ResearchKnowledgeAssistant/
│
├── frontend/
│   └── src/
│       ├── components/           # UploadForm, DocumentList, ChatBox, SourceSection
│       ├── pages/                # Login.jsx, Register.jsx, Dashboard.jsx, Chat.jsx
│       ├── services/             # api.js (Axios instance with JWT), documentApi.js, chatApi.js
│       ├── App.jsx               # Routes setup & Navigation layout
│       └── main.jsx              # React Entrypoint
│
├── backend/
│   ├── config/                   # db.js (MongoDB connection with Mongoose)
│   ├── controllers/              # authController.js, documentController.js, chatController.js
│   ├── middleware/              # authMiddleware.js (JWT verify), uploadMiddleware.js (Multer)
│   ├── models/                   # User.js, Document.js, Chat.js
│   ├── routes/                   # authRoutes.js, documentRoutes.js, chatRoutes.js
│   ├── uploads/                  # Local storage for uploaded PDF files
│   ├── app.js                    # Express app configuration & middleware
│   └── server.js                 # HTTP server entry point
│
└── ai_service/
    ├── core/                     # parser.py, heading_scorer.py, section_detector.py, metadata_builder.py
    ├── retrieval/                # chunker.py, embeddings.py, vector_store.py, retriever.py
    ├── generation/               # gemini_client.py
    ├── vector_stores/            # Saved FAISS indexes (.index and .pkl files)
    ├── main.py                   # FastAPI server entry point (/process-pdf & /query)
    └── requirements.txt          # Python dependencies
```

---

## 3. Simplified Database Schema (MongoDB Mongoose)

The persistence layer is simplified to **only three collections**:

### 3.1 `Users` Collection (`models/User.js`)
```javascript
{
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true }, // Encrypted with bcrypt
  createdAt: { type: Date, default: Date.now }
}
```

### 3.2 `Documents` Collection (`models/Document.js`)
```javascript
{
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  paperName: { type: String, required: true },
  filePath: { type: String, required: true }, // e.g. "uploads/1722765000-paper.pdf"
  status: { type: String, enum: ['PROCESSING', 'COMPLETED', 'FAILED'], default: 'PROCESSING' },
  createdAt: { type: Date, default: Date.now }
}
```

### 3.3 `Chats` Collection (`models/Chat.js`)
```javascript
{
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document', required: true },
  question: { type: String, required: true },
  answer: { type: String, required: true },
  retrievedSections: [
    {
      sectionTitle: String,
      pageNumber: Number,
      snippet: String
    }
  ],
  timestamp: { type: Date, default: Date.now }
}
```

---

## 4. Simplified REST API Specification

### 4.1 Node.js + Express Backend API Endpoints

| Method | Endpoint | Description | Request Body / Query | Auth Required |
| :--- | :--- | :--- | :--- | :--- |
| **POST** | `/api/register` | Register new user | `{ name, email, password }` | No |
| **POST** | `/api/login` | Login user & issue JWT | `{ email, password }` | No |
| **POST** | `/api/upload` | Upload PDF file | Multipart `file` | Yes (JWT) |
| **GET** | `/api/documents` | List user's uploaded papers | None | Yes (JWT) |
| **POST** | `/api/ask` | Submit question for a document | `{ documentId, question }` | Yes (JWT) |
| **GET** | `/api/history` | Get chat history for a document | Query param `?documentId=...` | Yes (JWT) |

### 4.2 Python FastAPI AI Service Internal Endpoints

| Method | Endpoint | Payload | Description |
| :--- | :--- | :--- | :--- |
| **POST** | `/process-pdf` | `{ "document_id": str, "file_path": str }` | Parses PDF, generates chunks & embeddings, saves FAISS index to `ai_service/vector_stores/`. |
| **POST** | `/query` | `{ "document_id": str, "query": str }` | Loads FAISS index, retrieves top context sections, queries Gemini LLM, returns answer + retrieved source sections. |

---

## 5. Frontend Pages & Components Breakdown

### 5.1 Pages
* **Login (`pages/Login.jsx`)**: Minimal form for user email and password with error feedback and navigation to Register.
* **Register (`pages/Register.jsx`)**: Registration form with name, email, password, creating new accounts.
* **Dashboard (`pages/Dashboard.jsx`)**: Main landing page after auth. Contains:
  - **Upload PDF Section**: File picker / drag-and-drop form triggering `POST /api/upload`.
  - **Uploaded Papers List**: Table/cards of documents showing `paperName`, `createdAt`, `status`, and button to "Open Chat".
* **Chat (`pages/Chat.jsx`)**: Interactive Q&A workspace for a selected document. Contains:
  - Document Title banner
  - Conversation history stream (Questions & Answers)
  - **Retrieved Source Sections**: Expandable / inline cards showing exact source snippets, page numbers, and section titles retrieved by RAG.
  - **Question Input Form**: Input box + send button triggering `POST /api/ask`.

---

## 6. Implementation Steps & Development Scope

### Phase 1: AI Service Standardization (FastAPI)
1. Organize existing Python files into `ai_service/core/`, `ai_service/retrieval/`, and `ai_service/generation/`.
2. Build `main.py` exposing `POST /process-pdf` and `POST /query`.
3. Verify vector storage creation in `ai_service/vector_stores/`.

### Phase 2: Express Backend Setup
1. Setup Express app with Mongoose connection to MongoDB.
2. Implement `User`, `Document`, and `Chat` schemas.
3. Build Auth middleware (JWT verification) and Multer middleware (`backend/uploads/`).
4. Implement controllers and wire up HTTP call to Python FastAPI using `axios`.

### Phase 3: React Frontend UI
1. Initialize Vite + React setup.
2. Build simple clean UI components for Auth, Dashboard, Upload, and Chat.
3. Wire frontend services to Express API endpoints.

---

## User Review Required

> [!NOTE]
> All enterprise microservice overhead (Docker, SSE streaming, GridFS, health checks, background workers) has been removed.
> The internal Python AI pipeline (`parser.py`, `heading_scorer.py`, `section_detector.py`, `metadata_builder.py`, `chunker.py`, `embeddings.py`, `vector_store.py`, `retriever.py`, `gemini_client.py`) remains 100% intact and untouched.

---

## Open Questions

None. The requirements and scope reduction have been fully aligned with a single-developer 1-2 week portfolio target.

---

## Proposed Changes

### AI Microservice (`ai_service/`)

#### [MODIFY] [main.py](file:///C:/Users/CSE/Desktop/ResearchKnowledgeAssisstant/ai_service/main.py)
Expose simple FastAPI app with `POST /process-pdf` and `POST /query`.

---

### Backend Gateway (`backend/`)

#### [NEW] [server.js](file:///C:/Users/CSE/Desktop/ResearchKnowledgeAssisstant/backend/server.js)
#### [NEW] [app.js](file:///C:/Users/CSE/Desktop/ResearchKnowledgeAssisstant/backend/app.js)
#### [NEW] [models/User.js](file:///C:/Users/CSE/Desktop/ResearchKnowledgeAssisstant/backend/models/User.js)
#### [NEW] [models/Document.js](file:///C:/Users/CSE/Desktop/ResearchKnowledgeAssisstant/backend/models/Document.js)
#### [NEW] [models/Chat.js](file:///C:/Users/CSE/Desktop/ResearchKnowledgeAssisstant/backend/models/Chat.js)
#### [NEW] [controllers/authController.js](file:///C:/Users/CSE/Desktop/ResearchKnowledgeAssisstant/backend/controllers/authController.js)
#### [NEW] [controllers/documentController.js](file:///C:/Users/CSE/Desktop/ResearchKnowledgeAssisstant/backend/controllers/documentController.js)
#### [NEW] [controllers/chatController.js](file:///C:/Users/CSE/Desktop/ResearchKnowledgeAssisstant/backend/controllers/chatController.js)

---

### Frontend SPA (`frontend/`)

#### [NEW] [src/pages/Login.jsx](file:///C:/Users/CSE/Desktop/ResearchKnowledgeAssisstant/frontend/src/pages/Login.jsx)
#### [NEW] [src/pages/Register.jsx](file:///C:/Users/CSE/Desktop/ResearchKnowledgeAssisstant/frontend/src/pages/Register.jsx)
#### [NEW] [src/pages/Dashboard.jsx](file:///C:/Users/CSE/Desktop/ResearchKnowledgeAssisstant/frontend/src/pages/Dashboard.jsx)
#### [NEW] [src/pages/Chat.jsx](file:///C:/Users/CSE/Desktop/ResearchKnowledgeAssisstant/frontend/src/pages/Chat.jsx)

---

## Verification Plan

### Automated Tests
- Test Python FastAPI endpoints using direct HTTP requests.
- Verify Express routes with Postman/curl.

### Manual Verification
- Test user flow: Register -> Login -> Upload PDF -> View in Dashboard -> Chat with PDF -> View source citations.
