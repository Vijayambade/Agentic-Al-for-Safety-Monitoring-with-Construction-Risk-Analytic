"""
backend/routers/document_analyzer.py
------------------------------------
FastAPI router for document analyzer uploads, audit reports, and RAG Q&A queries.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database import get_db
from backend.models.document import AnalyzedDocument
from backend.routers.auth import get_current_user
from backend.models.user import User
from backend.routers.ai import extract_text_from_file
from backend.services.analyzer_service import classify_document, audit_document
from backend.services.rag_service import create_vector_index, retrieve_relevant_chunks
from backend.services.ai_service import call_construction_llm

router = APIRouter(prefix="/api/v1/document-analyzer", tags=["Document Analyzer Chatbot"])


class QueryRequest(BaseModel):
    document_id: int
    question: str


class DocumentResponse(BaseModel):
    id: int
    filename: str
    doc_type: str
    summary: str
    missing_clauses: str
    risks: str
    recommendations: str


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a construction document, extract text, perform audits,
    and build a FAISS RAG index.
    """
    file_bytes = await file.read()
    filename = file.filename

    # 1. Extract raw text content
    try:
        raw_text = extract_text_from_file(filename, file_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse text from document: {str(e)}"
        )

    if not raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded document contains no readable text."
        )

    # 2. Classify document type
    doc_type = classify_document(filename, raw_text)

    # 3. Perform document audits (Summary, Clauses, Risks, Recs)
    audit_results = audit_document(filename, raw_text, doc_type)

    # 4. Save AnalyzedDocument to database (initially without index_path)
    db_doc = AnalyzedDocument(
        filename=filename,
        doc_type=doc_type,
        summary=audit_results["summary"],
        missing_clauses=audit_results["missing_clauses"],
        risks=audit_results["risks"],
        recommendations=audit_results["recommendations"],
        raw_text=raw_text
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    # 5. Compile FAISS index
    try:
        index_path = create_vector_index(db_doc.id, raw_text)
        db_doc.index_path = index_path
        db.commit()
    except Exception as e:
        # Log error but don't fail upload completely since database record exists
        import logging
        logging.getLogger(__name__).error("FAISS compilation failed: %s", e)

    return db_doc


@router.post("/query")
def query_document(
    schema: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Query the uploaded document using vector search (RAG).
    Returns contextual LLM response along with retrieved passages.
    """
    doc = db.query(AnalyzedDocument).filter(AnalyzedDocument.id == schema.document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analyzed document not found."
        )

    # 1. Retrieve matching passages from vector store
    context_chunks = retrieve_relevant_chunks(doc.id, schema.question)
    
    context_str = "\n---\n".join(context_chunks)

    # 2. Query AI model with context
    prompt = (
        f"Answer the user question below using the provided context from the construction document.\n"
        f"Context Chunks:\n"
        f"============================\n"
        f"{context_str}\n"
        f"============================\n\n"
        f"User Question: {schema.question}"
    )

    answer = call_construction_llm(prompt)

    return {
        "document_id": doc.id,
        "question": schema.question,
        "answer": answer,
        "context_retrieved": context_chunks
    }


@router.get("/list", response_model=List[DocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all audited documents."""
    return db.query(AnalyzedDocument).order_by(AnalyzedDocument.created_at.desc()).all()


@router.get("/details/{doc_id}", response_model=DocumentResponse)
def get_document_details(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full audit detail reports for a document."""
    doc = db.query(AnalyzedDocument).filter(AnalyzedDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
    return doc
