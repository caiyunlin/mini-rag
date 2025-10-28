from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import aiofiles

from ..models.schemas import QueryRequest, QueryResponse, DocumentResponse
from ..services.rag_service import RAGService

router = APIRouter()

# Dependency to get RAG service instance
async def get_rag_service():
    return RAGService()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    rag_service: RAGService = Depends(get_rag_service)
):
    """Upload and process a document."""
    try:
        # Read file content
        file_content = await file.read()
        
        # Process document
        result = await rag_service.upload_document(file_content, file.filename)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Query documents and get AI-generated response."""
    try:
        result = await rag_service.query_documents(request)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    rag_service: RAGService = Depends(get_rag_service)
):
    """List all documents in the system."""
    try:
        documents = await rag_service.list_documents()
        return documents
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Delete a document and all its chunks."""
    try:
        success = await rag_service.delete_document(document_id)
        if success:
            return {"message": "Document deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found or couldn't be deleted")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats")
async def get_system_stats(
    rag_service: RAGService = Depends(get_rag_service)
):
    """Get system statistics."""
    try:
        stats = await rag_service.get_system_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))