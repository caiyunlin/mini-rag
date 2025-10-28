import os
import uuid
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from .document_processor import DocumentProcessor
from .simple_document_store import SimpleDocumentStore
from .azure_ai import AzureAIService
from ..models.schemas import QueryRequest, QueryResponse, DocumentResponse


class RAGService:
    """Main RAG service that orchestrates document processing, vector storage, and AI generation."""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.document_store = SimpleDocumentStore()
        self.azure_ai = AzureAIService()
    
    async def upload_document(self, file_content: bytes, filename: str) -> DocumentResponse:
        """Process and store a document in the RAG system."""
        start_time = time.time()
        
        try:
            # Validate file
            is_valid, message = self.document_processor.validate_file(filename, len(file_content))
            if not is_valid:
                raise ValueError(message)
            
            # Save file
            file_path = await self.document_processor.save_file(file_content, filename)
            
            # Extract text
            text_content = self.document_processor.extract_text_from_file(file_path)
            
            # Generate document ID and metadata
            document_id = str(uuid.uuid4())
            metadata = {
                "source": filename,
                "file_path": file_path,
                "upload_time": datetime.now().isoformat(),
                "file_size": len(file_content)
            }
            
            # Add to document store
            success = await self.document_store.add_document(
                document_id, filename, text_content, metadata
            )
            
            if not success:
                raise Exception("Failed to store document")
            
            # Generate document summary
            summary = await self.azure_ai.summarize_document(text_content)
            
            processing_time = time.time() - start_time
            
            return DocumentResponse(
                id=document_id,
                filename=filename,
                content_preview=text_content[:500] + "..." if len(text_content) > 500 else text_content,
                upload_time=datetime.now(),
                metadata={
                    "processing_time": processing_time,
                    "summary": summary,
                    "file_size": len(file_content),
                    "storage_type": "markdown_file"
                }
            )
            
        except Exception as e:
            # Clean up file if it was saved but processing failed
            if 'file_path' in locals():
                try:
                    os.remove(file_path)
                except:
                    pass
            raise Exception(f"Error processing document: {str(e)}")
    
    async def query_documents(self, request: QueryRequest) -> QueryResponse:
        """Query the RAG system and generate a response."""
        start_time = time.time()
        
        try:
            # Perform simple text search
            relevant_docs = await self.document_store.search_documents(
                query=request.query,
                max_results=request.max_results
            )
            
            # Generate AI response
            answer = await self.azure_ai.generate_response(
                query=request.query,
                context_documents=relevant_docs
            )
            
            # Prepare source information
            sources = []
            for doc in relevant_docs:
                metadata = doc.get("metadata", {})
                sources.append({
                    "source": metadata.get("source", "Unknown"),
                    "document_id": metadata.get("document_id", ""),
                    "score": doc.get("score", 0),
                    "content_preview": doc.get("content", "")[:200] + "..."
                })
            
            response_time = time.time() - start_time
            
            return QueryResponse(
                query=request.query,
                answer=answer,
                sources=sources,
                response_time=response_time
            )
            
        except Exception as e:
            raise Exception(f"Error querying documents: {str(e)}")
    
    async def list_documents(self) -> List[DocumentResponse]:
        """List all documents in the system."""
        try:
            all_docs = await self.document_store.get_all_documents()
            
            document_responses = []
            for doc in all_docs:
                doc_metadata = doc.get("metadata", {})
                
                upload_time = doc_metadata.get("upload_time")
                if isinstance(upload_time, str):
                    try:
                        upload_time = datetime.fromisoformat(upload_time.replace('Z', '+00:00'))
                    except:
                        upload_time = datetime.now()
                else:
                    upload_time = datetime.now()
                
                document_responses.append(DocumentResponse(
                    id=doc["id"],
                    filename=doc_metadata.get("source", "Unknown"),
                    content_preview=doc.get("content", ""),
                    upload_time=upload_time,
                    metadata={
                        "chunks_count": doc_metadata.get("chunks_count", 0),
                        "content_length": doc_metadata.get("content_length", 0),
                        "storage_type": "markdown"
                    }
                ))
            
            return document_responses
            
        except Exception as e:
            raise Exception(f"Error listing documents: {str(e)}")
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document."""
        try:
            return await self.document_store.delete_document(document_id)
            
        except Exception as e:
            print(f"Error deleting document {document_id}: {str(e)}")
            return False
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        try:
            store_stats = self.document_store.get_store_stats()
            documents = await self.list_documents()
            
            return {
                "total_documents": len(documents),
                "total_chunks": store_stats.get("total_chunks", 0),
                "document_store_stats": store_stats,
                "system_status": "operational"
            }
            
        except Exception as e:
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "vector_store_stats": {},
                "system_status": "error",
                "error": str(e)
            }