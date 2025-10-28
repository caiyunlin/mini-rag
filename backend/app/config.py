from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Azure AI Foundry Configuration
    azure_ai_endpoint: Optional[str] = None
    azure_ai_key: Optional[str] = None
    azure_ai_model_name: str = "gpt-4"
    
    # Azure OpenAI Configuration (alternative)
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_deployment_name: Optional[str] = None
    
    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    
    # Document Processing Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # File Upload Configuration
    max_file_size: int = 10485760  # 10MB
    allowed_extensions: str = "pdf,txt,docx,md"
    
    # Data Paths
    data_dir: str = "/app/data"
    uploads_dir: str = "/app/data/uploads"
    vectorstore_dir: str = "/app/data/vectorstore"

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        os.makedirs(self.uploads_dir, exist_ok=True)
        os.makedirs(self.vectorstore_dir, exist_ok=True)

    @property
    def allowed_extensions_list(self):
        return [ext.strip() for ext in self.allowed_extensions.split(",")]


settings = Settings()