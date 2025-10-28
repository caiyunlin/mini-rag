from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DocumentUpload(BaseModel):
    content: str
    metadata: Optional[dict] = None


class DocumentResponse(BaseModel):
    id: str
    filename: str
    content_preview: str
    upload_time: datetime
    metadata: Optional[dict] = None


class QueryRequest(BaseModel):
    query: str
    max_results: int = 5
    similarity_threshold: float = 0.7


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[dict]
    response_time: float


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime