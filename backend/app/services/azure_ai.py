import asyncio
from typing import List, Dict, Any, Optional
import openai

from ..config import settings


class AzureAIService:
    """Handle Azure AI Foundry integration for RAG system."""
    
    def __init__(self):
        self.client = None
        self.openai_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Azure AI clients."""
        try:
            # Initialize Azure OpenAI client
            if settings.azure_openai_endpoint and settings.azure_openai_api_key:
                self.openai_client = openai.AzureOpenAI(
                    api_key=settings.azure_openai_api_key,
                    api_version=settings.azure_openai_api_version,
                    azure_endpoint=settings.azure_openai_endpoint
                )
            else:
                print("Warning: No Azure OpenAI credentials configured")
                self.openai_client = None
                
        except Exception as e:
            print(f"Warning: Azure AI client initialization failed: {e}")
            print("Using mock responses for development")
            self.openai_client = None
    
    async def generate_response(
        self, 
        query: str, 
        context_documents: List[Dict[str, Any]],
        max_tokens: int = 1000
    ) -> str:
        """Generate response using Azure AI with RAG context."""
        
        # Prepare context from retrieved documents
        context = self._prepare_context(context_documents)
        
        # If no context found, return a clear message
        if not context or context.strip() == "":
            return "Based on your uploaded documents, I cannot find relevant information to answer your question. Please ensure the relevant content has been uploaded to the knowledge base."
        
        # Create prompt with context
        prompt = self._create_rag_prompt(query, context)
        
        try:
            if self.openai_client:
                return await self._generate_with_openai(prompt, max_tokens)
            else:
                return self._mock_response(query, context)
                
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Sorry, an error occurred while generating the response: {str(e)}"
    
    async def _generate_with_openai(self, prompt: str, max_tokens: int) -> str:
        """Generate response using Azure OpenAI."""
        try:
            # Use deployment name if available, otherwise use model name
            model_name = settings.azure_openai_deployment_name or settings.azure_ai_model_name or "gpt-4"
            
            # Set system message for English responses
            system_message = "You are a Virtual Mentor, a knowledge base assistant. Please answer questions in English only, based on the provided context. Be helpful, clear, and professional."
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Azure OpenAI API error: {str(e)}")
    
    def _prepare_context(self, documents: List[Dict[str, Any]]) -> str:
        """Prepare context string from retrieved documents."""
        if not documents:
            return ""
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "").strip()
            source = doc.get("metadata", {}).get("source", "Unknown")
            if content:  # Only add non-empty content
                context_parts.append(f"[来源 {i}: {source}]\n{content}")
        
        return "\n\n".join(context_parts)
    
    def _create_rag_prompt(self, query: str, context: str) -> str:
        """Create RAG prompt with query and context."""
        if not context or context.strip() == "":
            return ""  # No context available
            
        prompt = f"""You are Virtual Mentor, a knowledge base assistant. Please answer the user's question strictly based on the provided context information.

Important rules:
1. Only use the provided context information to answer questions
2. Do not use your pre-trained knowledge to answer
3. If there is no relevant information in the context, clearly state "Based on the provided documents, I cannot find relevant information to answer this question"
4. When answering, please indicate which source the information comes from
5. Answer in English only
6. Be helpful, clear, and professional in your responses
7. You may quote code examples or technical content exactly as it appears in the documents

Context information:
{context}

User question: {query}

Please answer based on the above context information:"""
        
        return prompt
    
    def _mock_response(self, query: str, context: str) -> str:
        """Generate mock response for development/testing."""
        return f"""Virtual Mentor - Mock Response for development:

Query: {query}

Based on the available context, this is a simulated response. In a production environment, this would be generated by Azure AI Foundry or Azure OpenAI.

Context summary: {len(context)} characters of context were provided.

To enable real AI responses, please configure your Azure AI credentials in the .env file."""

    async def summarize_document(self, text: str, max_length: int = 200) -> str:
        """Generate a summary of the document."""
        prompt = f"""Please provide a concise summary of the following text in no more than {max_length} words:

{text[:2000]}  # Limit input text to avoid token limits

Summary:"""

        try:
            if self.openai_client:
                return await self._generate_with_openai(prompt, max_length)
            else:
                return f"Document summary (mock): This document contains approximately {len(text.split())} words."
                
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Summary unavailable. Document length: {len(text)} characters."