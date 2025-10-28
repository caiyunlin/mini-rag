# Virtual Mentor - AI Knowledge Assistant

A lightweight, document-based AI knowledge assistant powered by Azure OpenAI. Upload documents and get intelligent answers based strictly on your uploaded content.

## ✨ Features

- 🧠 **AI-Powered**: Uses Azure OpenAI for intelligent responses
- 📚 **Document Upload**: Support for PDF, TXT, DOCX, and MD files  
- 🔍 **Smart Search**: Simple text-based search without heavy vector databases
- 🌐 **Web Interface**: Clean, modern Bootstrap 5 UI
- 🐳 **Docker Ready**: Easy deployment with Docker/Docker Compose
- 🔒 **Source-Based**: Only answers based on uploaded documents
- 📱 **Responsive Design**: Works seamlessly across devices
- 🚀 **Fast Performance**: Optimized for quick responses
- 📊 **Simple Architecture**: No complex vector databases required

## 📋 Requirements

- Python 3.11+
- Docker and Docker Compose (optional)
- Azure OpenAI account

## 🛠️ Installation & Deployment

### Method 1: Docker Deployment (Recommended)

1. **Clone Repository**
   ```bash
   git clone https://github.com/caiyunlin/mini-rag.git
   cd mini-rag
   ```

2. **Configure Environment**
   ```bash
   cp .env.template .env
   # Edit .env file with your Azure OpenAI configuration
   ```

3. **Start Services**
   ```bash
   docker-compose up -d
   ```

4. **Access Application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Method 2: Local Development Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.template .env
   # Edit .env file
   ```

3. **Start Application**
   ```bash
   python run.py
   ```

## ⚙️ Configuration

### Azure OpenAI Setup

Configure the following parameters in your `.env` file:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
```

### Other Configuration Options

```env
# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True

# File Upload Settings
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=pdf,txt,docx,md

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## 🎯 Usage Guide

### Web Interface

1. **Upload Documents**
   - Click on the "Document Upload" area
   - Select supported file formats (PDF, TXT, DOCX, MD)
   - Click "Upload Document"

2. **Ask Questions**
   - Enter your question in the "Ask Virtual Mentor" area
   - Adjust query parameters (optional)
   - Click "Submit Query"

3. **Document Management**
   - View uploaded document list
   - Delete unwanted documents

### API Usage

#### Upload Document
```bash
curl -X POST "http://localhost:8000/api/v1/rag/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"
```

#### Query Q&A
```bash
curl -X POST "http://localhost:8000/api/v1/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Your question here",
    "max_results": 5,
    "similarity_threshold": 0.7
  }'
```

#### Get Document List
```bash
curl -X GET "http://localhost:8000/api/v1/rag/documents"
```

## 📁 Project Structure

```
mini-rag/
├── backend/                 # Backend API service
│   ├── app/
│   │   ├── models/         # Data models
│   │   ├── routers/        # API routes
│   │   ├── services/       # Business logic
│   │   ├── config.py       # Configuration management
│   │   └── main.py         # Main application
│   └── __init__.py
├── frontend/               # Frontend interface
│   ├── static/            # Static assets
│   │   ├── css/
│   │   └── js/
│   └── templates/         # HTML templates
├── data/                  # Data directory
│   ├── uploads/           # Uploaded files
│   └── documents/         # Document storage
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile            # Docker image configuration
├── requirements.txt      # Python dependencies
├── .env.template        # Environment variables template
├── run.py              # Startup script
└── README.md           # Project documentation
```

## 🔧 Tech Stack

- **Backend Framework**: FastAPI
- **AI Integration**: Azure OpenAI
- **Document Storage**: File-based with JSON indexing
- **Document Processing**: PyPDF, python-docx, BeautifulSoup4
- **Search Engine**: Text-based with keyword extraction
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Deployment**: Docker, Docker Compose

## 🐛 Troubleshooting

### Common Issues

1. **Azure OpenAI Connection Failed**
   - Check Azure configuration in `.env` file
   - Verify API key and endpoint URL are correct
   - Check network connectivity

2. **Document Upload Failed**
   - Check if file size exceeds limit (default 10MB)
   - Confirm file format is supported
   - Check available disk space

3. **Search Returns No Results**
   - Ensure relevant documents are uploaded
   - Try different keywords or phrases
   - Check document content language matches query

4. **Docker Container Failed to Start**
   - Check if port is already in use
   - Confirm Docker service is running
   - View container logs: `docker-compose logs`

### Viewing Logs

```bash
# View application logs
docker-compose logs mini-rag-api

# Real-time log monitoring
docker-compose logs -f
```

## 📈 Performance Optimization

1. **Document Processing Optimization**
   - Adjust document chunk size and overlap ratio
   - Optimize processing logic for specific document types
   - Implement caching for processed documents

2. **Search Performance**
   - Fine-tune keyword extraction algorithms
   - Implement result caching for common queries
   - Optimize document indexing

3. **Deployment Optimization**
   - Use Redis for query result caching
   - Configure load balancers for production
   - Optimize Docker image size and layers

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://github.com/tiangolo/fastapi) - Modern web framework
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) - AI services
- [Bootstrap](https://getbootstrap.com/) - Frontend framework
- [Python Community](https://www.python.org/) - Amazing ecosystem

## 📞 Support & Feedback

For questions or suggestions:
1. Create an [Issue](https://github.com/caiyunlin/mini-rag/issues)
2. Send email to: [your-email@example.com]
3. Join [Discussions](https://github.com/caiyunlin/mini-rag/discussions)

---

⭐ If this project helps you, please give it a star!
