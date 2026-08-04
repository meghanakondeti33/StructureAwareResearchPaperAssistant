import sys
import os
import pickle
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add project root and ai_service directories to sys.path so existing `src.*` imports resolve seamlessly
root_dir = Path(__file__).resolve().parent.parent
ai_service_dir = Path(__file__).resolve().parent

if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(ai_service_dir) not in sys.path:
    sys.path.insert(0, str(ai_service_dir))

from ai_service.core.parser import PDFParser
from ai_service.core.section_detector import SectionDetector
from ai_service.core.metadata_builder import MetadataBuilder
from ai_service.retrieval.chunker import SectionChunker
from ai_service.retrieval.embeddings import EmbeddingGenerator
from ai_service.retrieval.vector_store import VectorStore
from ai_service.retrieval.retriever import Retriever
from ai_service.generation.gemini_client import GeminiClient

app = FastAPI(title="ResearchKnowledgeAssistant AI Service")

# Lazy-loaded singletons to optimize memory & query performance
_embedder = None
_retriever = None
_gemini_client = None


def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = EmbeddingGenerator()
    return _embedder


def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


def get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client


class ProcessPDFRequest(BaseModel):
    document_id: str
    file_path: str


class QueryRequest(BaseModel):
    document_id: str
    query: str


@app.get("/")
def read_root():
    return {"status": "ok", "service": "AI Microservice"}


@app.post("/process-pdf")
def process_pdf(req: ProcessPDFRequest):
    try:
        pdf_path = req.file_path
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail=f"PDF File not found at path: {pdf_path}")

        # 1. Parse PDF Layout Elements
        parser = PDFParser(pdf_path)
        elements = parser.extract_elements()

        # 2. Detect Headings & Sections
        detector = SectionDetector()
        headings = detector.detect_sections(elements)

        # 3. Build Metadata & Section Text
        builder = MetadataBuilder()
        sections = builder.build_sections(elements, headings)

        # Fallback if no headings detected: treat full document text as single section
        if not sections:
            full_text = " ".join([elem["text"] for elem in elements])
            sections = [{"title": "Full Document", "page": 0, "content": full_text}]

        # 4. Create Section-Aware Chunks
        chunker = SectionChunker()
        chunks = chunker.chunk_sections(sections)

        # 5. Generate Dense Embeddings
        embedder = get_embedder()
        embeddings = embedder.embed_chunks(chunks)

        # 6. Build and Save FAISS Index & Chunks PKL
        vector_store = VectorStore()
        vector_store.build_index(embeddings)

        vector_stores_dir = os.path.join(ai_service_dir, "vector_stores")
        os.makedirs(vector_stores_dir, exist_ok=True)

        index_path = os.path.join(vector_stores_dir, f"{req.document_id}.index")
        pkl_path = os.path.join(vector_stores_dir, f"{req.document_id}.pkl")

        vector_store.save_index(index_path)

        with open(pkl_path, "wb") as f:
            pickle.dump(chunks, f)

        return {
            "status": "success",
            "document_id": req.document_id,
            "num_sections": len(sections),
            "num_chunks": len(chunks),
            "index_path": index_path,
            "pkl_path": pkl_path,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
def query(req: QueryRequest):
    try:
        vector_stores_dir = os.path.join(ai_service_dir, "vector_stores")
        index_path = os.path.join(vector_stores_dir, f"{req.document_id}.index")
        pkl_path = os.path.join(vector_stores_dir, f"{req.document_id}.pkl")

        if not os.path.exists(index_path) or not os.path.exists(pkl_path):
            raise HTTPException(
                status_code=404,
                detail=f"FAISS index or chunk metadata not found for document {req.document_id}. Please upload/process PDF first.",
            )

        # 1. Load serialized chunks
        with open(pkl_path, "rb") as f:
            chunks = pickle.load(f)

        # 2. Load FAISS index & retrieve top chunks
        retriever = get_retriever()
        retriever.load(index_path)

        retrieved_results = retriever.retrieve(
            query=req.query,
            chunks=chunks,
            top_k=5,
        )

        # 3. Generate RAG answer using Gemini API
        gemini = get_gemini_client()
        answer = gemini.generate_answer(
            question=req.query,
            retrieved_chunks=retrieved_results,
        )

        # 4. Format retrieved sections for client presentation
        retrieved_sections = [
            {
                "sectionTitle": item["chunk"].get("title", "Unknown Section"),
                "pageNumber": item["chunk"].get("page", 0) + 1,
                "snippet": item["chunk"].get("content", ""),
                "score": round(float(item.get("score", 0.0)), 4),
            }
            for item in retrieved_results
        ]

        return {
            "status": "success",
            "document_id": req.document_id,
            "query": req.query,
            "answer": answer,
            "retrieved_sections": retrieved_sections,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Query Execution Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
