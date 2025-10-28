# Virtual Mentor - Docker Deployment Guide

## Quick Start

### 1. Using Docker Run

```bash
# Basic run (without data persistence)
docker run -p 8000:8000 --env-file .env cylin2000/mini-rag

# With data persistence (recommended)
docker run -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  cylin2000/mini-rag

# Windows PowerShell version
docker run -p 8000:8000 --env-file .env -v ${PWD}/data:/app/data cylin2000/mini-rag
```

### 2. Using Docker Compose (recommended)

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

## Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your Azure AI credentials:
   ```properties
   AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   ```

## Important Notes

### Environment File Format
- **No inline comments**: Don't use `MAX_FILE_SIZE=10485760 # 10MB`
- **Correct format**: Use `MAX_FILE_SIZE=10485760`
- **No quotes needed**: Values are automatically parsed

### Data Persistence
To persist uploaded documents and data:
```bash
# Create data directory
mkdir -p ./data/uploads ./data/vectorstore

# Run with volume mount
docker run -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  cylin2000/mini-rag
```

### Common Issues

1. **Pydantic Validation Error**
   - Issue: `MAX_FILE_SIZE=10485760  # 10MB`
   - Fix: Remove inline comments from .env file

2. **Azure AI Connection Issues**
   - Verify your endpoint URL format
   - Check API key validity
   - Ensure deployment name matches your Azure setup

3. **Port Already in Use**
   - Change port mapping: `-p 8001:8000`
   - Or stop conflicting services

## Accessing the Application

- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Building Custom Image

```bash
# Build from source
git clone <repository-url>
cd mini-rag
docker build -t virtual-mentor .

# Run custom image
docker run -p 8000:8000 --env-file .env virtual-mentor
```

## Production Deployment

For production use, consider:

1. **Use HTTPS**: Set up reverse proxy (nginx, traefik)
2. **Resource Limits**: Add memory and CPU limits
3. **Monitoring**: Set up logging and metrics
4. **Backup**: Regular backup of data directory
5. **Security**: Use secrets management instead of .env files

Example production command:
```bash
docker run -d \
  --name virtual-mentor \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env \
  -v /data/virtual-mentor:/app/data \
  --memory=2g \
  --cpus=1.0 \
  cylin2000/mini-rag
```