import os
import uuid
from typing import List, Optional
from pathlib import Path
import aiofiles
import pypdf
import docx
import markdown
from bs4 import BeautifulSoup

from ..config import settings


class DocumentProcessor:
    """Handle document processing and text extraction."""
    
    def __init__(self):
        self.allowed_extensions = settings.allowed_extensions_list
        
    async def save_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file and return file path."""
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(filename).suffix.lower()
        new_filename = f"{file_id}_{filename}"
        file_path = os.path.join(settings.uploads_dir, new_filename)
        
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)
            
        return file_path
    
    def validate_file(self, filename: str, file_size: int) -> tuple[bool, str]:
        """Validate file extension and size."""
        file_extension = Path(filename).suffix.lower().lstrip(".")
        
        if file_extension not in self.allowed_extensions:
            return False, f"File type .{file_extension} not allowed. Allowed types: {', '.join(self.allowed_extensions)}"
        
        if file_size > settings.max_file_size:
            return False, f"File size {file_size} exceeds maximum allowed size {settings.max_file_size}"
        
        return True, "Valid file"
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file formats."""
        file_extension = Path(file_path).suffix.lower()
        
        try:
            if file_extension == ".pdf":
                return self._extract_from_pdf(file_path)
            elif file_extension == ".docx":
                return self._extract_from_docx(file_path)
            elif file_extension == ".txt":
                return self._extract_from_txt(file_path)
            elif file_extension == ".md":
                return self._extract_from_markdown(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
        except Exception as e:
            raise Exception(f"Error extracting text from {file_path}: {str(e)}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        with open(file_path, "rb") as file:
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    
    def _extract_from_markdown(self, file_path: str) -> str:
        """Extract text from Markdown file."""
        with open(file_path, "r", encoding="utf-8") as file:
            md_content = file.read()
            # Convert markdown to HTML and then extract text
            html = markdown.markdown(md_content)
            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text()
    
    def split_text_into_chunks(self, text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[str]:
        """Split text into chunks for vector embedding."""
        chunk_size = chunk_size or settings.chunk_size
        chunk_overlap = chunk_overlap or settings.chunk_overlap
        
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