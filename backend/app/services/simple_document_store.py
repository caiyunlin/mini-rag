import os
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..config import settings


class SimpleDocumentStore:
    """Simple file-based document storage without vector embeddings."""
    
    def __init__(self):
        self.documents_file = os.path.join(settings.data_dir, "documents.json")
        self.markdown_dir = os.path.join(settings.data_dir, "markdown")
        os.makedirs(self.markdown_dir, exist_ok=True)
        
        # Load existing documents index
        self.documents_index = self._load_documents_index()
    
    def _load_documents_index(self) -> Dict[str, Any]:
        """Load documents index from JSON file."""
        if os.path.exists(self.documents_file):
            try:
                with open(self.documents_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading documents index: {e}")
                return {}
        return {}
    
    def _save_documents_index(self):
        """Save documents index to JSON file."""
        try:
            with open(self.documents_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents_index, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"Error saving documents index: {e}")
    
    async def add_document(self, document_id: str, filename: str, content: str, metadata: Dict[str, Any]) -> bool:
        """Add a document to the simple store."""
        try:
            # Split content into chunks
            chunks = self._split_text_into_chunks(content)
            
            # Save as markdown file
            markdown_file = os.path.join(self.markdown_dir, f"{document_id}.md")
            
            # Create markdown content with metadata
            markdown_content = f"""# {filename}

**文档ID**: {document_id}
**上传时间**: {datetime.now().isoformat()}
**文件大小**: {len(content)} 字符
**分块数量**: {len(chunks)}

---

{content}

---

## 文档分块

"""
            
            # Add chunks as sections
            for i, chunk in enumerate(chunks):
                markdown_content += f"""### 分块 {i+1}

{chunk}

---

"""
            
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # Update index
            self.documents_index[document_id] = {
                "filename": filename,
                "markdown_file": markdown_file,
                "upload_time": datetime.now().isoformat(),
                "content_length": len(content),
                "chunks_count": len(chunks),
                "metadata": metadata
            }
            
            self._save_documents_index()
            return True
            
        except Exception as e:
            print(f"Error adding document: {e}")
            return False
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Simple text chunking without embeddings."""
        chunk_size = settings.chunk_size
        chunk_overlap = settings.chunk_overlap
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Find the last period within the chunk
                last_period = text.rfind(".", start, end)
                if last_period != -1 and last_period > start + chunk_size // 2:
                    end = last_period + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query for better matching."""
        # Common stop words to ignore
        stop_words = {'的', '是', '在', '有', '和', '与', '或', '但', '然后', '如何', '什么', '怎么', '怎样', 
                     'how', 'to', 'what', 'is', 'are', 'the', 'a', 'an', 'and', 'or', 'but', 'then'}
        
        # Split query and filter out stop words and short words
        keywords = []
        for word in query.split():
            word = word.strip('.,!?;:()[]{}"\'-')
            if len(word) >= 2 and word.lower() not in stop_words:
                keywords.append(word.lower())
        
        return keywords
    
    async def search_documents(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Simple text search without vector similarity."""
        results = []
        query_lower = query.lower()
        
        # Extract keywords from query for better matching
        query_keywords = self._extract_keywords(query_lower)
        print(f"🔍 Search query: '{query}' | Keywords: {query_keywords}")
        
        for doc_id, doc_info in self.documents_index.items():
            try:
                markdown_file = doc_info["markdown_file"]
                if not os.path.exists(markdown_file):
                    continue
                
                with open(markdown_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Multiple matching strategies
                content_lower = content.lower()
                score = 0
                
                # 1. Exact phrase matching
                if query_lower in content_lower:
                    score += 10
                
                # 2. Keyword matching
                keyword_matches = 0
                for keyword in query_keywords:
                    if keyword in content_lower:
                        keyword_matches += 1
                        score += 3
                
                # Only include if we have matches
                if score > 0:
                    # Find relevant chunks
                    lines = content.split('\n')
                    relevant_chunks = []
                    
                    # Look for lines containing query keywords
                    for i, line in enumerate(lines):
                        line_lower = line.lower()
                        line_matches = False
                        
                        # Check for exact phrase or keyword matches
                        if query_lower in line_lower:
                            line_matches = True
                        else:
                            # Check if line contains multiple keywords
                            matches = sum(1 for keyword in query_keywords if keyword in line_lower)
                            if matches >= 2 or (matches >= 1 and len(query_keywords) <= 2):
                                line_matches = True
                        
                        if line_matches:
                            # Get context around the match
                            start_idx = max(0, i - 3)
                            end_idx = min(len(lines), i + 4)
                            context = '\n'.join(lines[start_idx:end_idx]).strip()
                            if context and len(context) > 10:  # Only meaningful context
                                relevant_chunks.append(context[:400] + "..." if len(context) > 400 else context)
                    
                    # If no specific chunks found, use broader content
                    if not relevant_chunks:
                        # Get content sections that contain keywords
                        sections = content.split('\n\n')
                        for section in sections:
                            section_lower = section.lower()
                            matches = sum(1 for keyword in query_keywords if keyword in section_lower)
                            if matches >= 1:
                                relevant_chunks.append(section[:400] + "..." if len(section) > 400 else section)
                    
                    print(f"📄 Document {doc_info['filename']}: score={score}, chunks={len(relevant_chunks)}")
                    
                    if relevant_chunks:  # Only add if we found relevant content
                        results.append({
                            "content": '\n\n'.join(relevant_chunks[:3]),  # Limit to top 3 chunks
                            "metadata": {
                                "document_id": doc_id,
                                "source": doc_info["filename"],
                                "upload_time": doc_info["upload_time"]
                            },
                            "score": score
                        })
                    
            except Exception as e:
                print(f"Error searching document {doc_id}: {e}")
                continue
        
        # Sort by score and limit results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
    
    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents from the simple store."""
        documents = []
        
        for doc_id, doc_info in self.documents_index.items():
            try:
                # Read content preview from markdown file
                markdown_file = doc_info["markdown_file"]
                content_preview = ""
                
                if os.path.exists(markdown_file):
                    with open(markdown_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Extract original content (after first ---)
                        parts = content.split('---', 2)
                        if len(parts) > 2:
                            original_content = parts[1].strip()
                            content_preview = original_content[:500] + "..." if len(original_content) > 500 else original_content
                
                documents.append({
                    "id": doc_id,
                    "content": content_preview,
                    "metadata": doc_info
                })
                
            except Exception as e:
                print(f"Error getting document {doc_id}: {e}")
                continue
        
        return documents
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from the simple store."""
        try:
            if document_id in self.documents_index:
                doc_info = self.documents_index[document_id]
                
                # Delete markdown file
                markdown_file = doc_info["markdown_file"]
                if os.path.exists(markdown_file):
                    os.remove(markdown_file)
                
                # Remove from index
                del self.documents_index[document_id]
                self._save_documents_index()
                
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting document {document_id}: {e}")
            return False
    
    def get_store_stats(self) -> Dict[str, Any]:
        """Get simple store statistics."""
        total_docs = len(self.documents_index)
        total_chunks = sum(doc_info.get("chunks_count", 0) for doc_info in self.documents_index.values())
        
        return {
            "total_documents": total_docs,
            "total_chunks": total_chunks,
            "storage_type": "markdown_files",
            "markdown_directory": self.markdown_dir
        }