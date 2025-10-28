// Mini-RAG Frontend JavaScript

class MiniRAGApp {
    constructor() {
        this.baseURL = '/api/v1/rag';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSystemStats();
        this.loadDocuments();
    }

    bindEvents() {
        // Upload form
        document.getElementById('upload-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.uploadDocument();
        });

        // Query form
        document.getElementById('query-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.queryDocuments();
        });

        // Auto-refresh stats every 30 seconds
        setInterval(() => {
            this.loadSystemStats();
        }, 30000);
    }

    async loadSystemStats() {
        try {
            const response = await fetch(`${this.baseURL}/stats`);
            const stats = await response.json();

            document.getElementById('total-documents').textContent = stats.total_documents || 0;
            document.getElementById('total-chunks').textContent = stats.total_chunks || 0;
            
            document.getElementById('embedding-model').textContent = 'Text Search';
            
            const statusElement = document.getElementById('system-status');
            if (stats.system_status === 'operational') {
                statusElement.className = 'badge bg-success fs-6';
                statusElement.textContent = 'Running';
            } else {
                statusElement.className = 'badge bg-danger fs-6';
                statusElement.textContent = 'Error';
            }
        } catch (error) {
            console.error('Failed to load system stats:', error);
            this.showToast('Failed to load system status', 'error');
        }
    }

    async loadDocuments() {
        try {
            const response = await fetch(`${this.baseURL}/documents`);
            const documents = await response.json();

            const listContainer = document.getElementById('documents-list');
            
            if (documents.length === 0) {
                listContainer.innerHTML = `
                    <div class="list-group-item text-center text-muted">
                        <i class="fas fa-folder-open fa-2x mb-2"></i>
                        <p class="mb-0">No documents yet</p>
                    </div>
                `;
                return;
            }

            listContainer.innerHTML = documents.map(doc => `
                <div class="list-group-item document-item" data-id="${doc.id}">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="mb-1">${this.escapeHtml(doc.filename)}</h6>
                            <p class="mb-1 text-truncate-2">${this.escapeHtml(doc.content_preview)}</p>
                            <div class="document-meta">
                                <i class="fas fa-clock me-1"></i>
                                ${this.formatDate(doc.upload_time)}
                                ${doc.metadata?.total_chunks ? `<span class="ms-2"><i class="fas fa-puzzle-piece me-1"></i>${doc.metadata.total_chunks} chunks</span>` : ''}
                            </div>
                        </div>
                        <div class="ms-2">
                            <button class="btn btn-sm btn-outline-danger" onclick="app.deleteDocument('${doc.id}')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Failed to load documents:', error);
            this.showToast('Failed to load documents', 'error');
        }
    }

    async uploadDocument() {
        const fileInput = document.getElementById('file-input');
        const file = fileInput.files[0];

        if (!file) {
            this.showToast('Please select a file to upload', 'warning');
            return;
        }

        const progressContainer = document.getElementById('upload-progress');
        const progressBar = progressContainer.querySelector('.progress-bar');
        
        progressContainer.style.display = 'block';
        progressBar.style.width = '0%';

        const formData = new FormData();
        formData.append('file', file);

        try {
            // Simulate progress
            const progressInterval = setInterval(() => {
                const currentWidth = parseInt(progressBar.style.width) || 0;
                if (currentWidth < 90) {
                    progressBar.style.width = (currentWidth + 10) + '%';
                }
            }, 200);

            const response = await fetch(`${this.baseURL}/upload`, {
                method: 'POST',
                body: formData
            });

            clearInterval(progressInterval);
            progressBar.style.width = '100%';

            if (response.ok) {
                const result = await response.json();
                this.showToast(`Document "${result.filename}" uploaded successfully!`, 'success');
                fileInput.value = '';
                setTimeout(() => {
                    progressContainer.style.display = 'none';
                    progressBar.style.width = '0%';
                }, 1000);
                this.loadDocuments();
                this.loadSystemStats();
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Upload failed');
            }
        } catch (error) {
            console.error('Upload failed:', error);
            this.showToast(`Upload failed: ${error.message}`, 'error');
            progressContainer.style.display = 'none';
        }
    }

    async queryDocuments() {
        const queryInput = document.getElementById('query-input');
        const query = queryInput.value.trim();

        if (!query) {
            this.showToast('Please enter a question', 'warning');
            return;
        }

        const maxResults = parseInt(document.getElementById('max-results').value) || 5;
        const similarityThreshold = parseFloat(document.getElementById('similarity-threshold').value) || 0.7;

        const resultsContainer = document.getElementById('query-results');
        
        // Show loading state
        resultsContainer.innerHTML = `
            <div class="text-center">
                <div class="loading me-2"></div>
                <span>Thinking...</span>
            </div>
        `;

        try {
            const response = await fetch(`${this.baseURL}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    max_results: maxResults,
                    similarity_threshold: similarityThreshold
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.displayQueryResults(result);
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Query failed');
            }
        } catch (error) {
            console.error('Query failed:', error);
            resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Query failed: ${error.message}
                </div>
            `;
        }
    }

    displayQueryResults(result) {
        const resultsContainer = document.getElementById('query-results');
        
        const sourcesHtml = result.sources.length > 0 ? `
            <div class="query-sources mt-3">
                <h6><i class="fas fa-book me-2"></i>Sources</h6>
                ${result.sources.map(source => `
                    <div class="source-item">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <strong>${this.escapeHtml(source.source)}</strong>
                                <span class="source-score ms-2 badge bg-info">${(source.score * 100).toFixed(1)}%</span>
                                <p class="mb-0 mt-1 text-muted small">${this.escapeHtml(source.content_preview)}</p>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        ` : `
            <div class="alert alert-warning mt-3">
                <i class="fas fa-info-circle me-2"></i>
                No relevant documents found
            </div>
        `;

        resultsContainer.innerHTML = `
            <div class="query-result fade-in">
                <div class="mb-3">
                    <strong>Question:</strong> ${this.escapeHtml(result.query)}
                    <span class="badge bg-secondary ms-2">${(result.response_time * 1000).toFixed(0)}ms</span>
                </div>
                
                <div class="query-answer">
                    <h6><i class="fas fa-user-graduate me-2"></i>Virtual Mentor</h6>
                    <div class="mt-2">${this.formatText(result.answer)}</div>
                </div>
                
                ${sourcesHtml}
            </div>
        `;
    }

    async deleteDocument(documentId) {
        if (!confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`${this.baseURL}/documents/${documentId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('Document deleted successfully', 'success');
                this.loadDocuments();
                this.loadSystemStats();
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Delete failed');
            }
        } catch (error) {
            console.error('Delete failed:', error);
            this.showToast(`Delete failed: ${error.message}`, 'error');
        }
    }

    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        const toastBody = document.getElementById('toast-body');
        const toastHeader = toast.querySelector('.toast-header i');

        // Update icon and color based on type
        toastHeader.className = `fas me-2 ${
            type === 'success' ? 'fa-check-circle text-success' :
            type === 'error' ? 'fa-exclamation-circle text-danger' :
            type === 'warning' ? 'fa-exclamation-triangle text-warning' :
            'fa-info-circle text-primary'
        }`;

        toastBody.textContent = message;
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatText(text) {
        // Simple text formatting (convert newlines to breaks)
        return this.escapeHtml(text).replace(/\n/g, '<br>');
    }

    formatDate(dateString) {
        try {
            const date = new Date(dateString);
            return date.toLocaleString('en-US', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            return dateString;
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MiniRAGApp();
});

// Global function for template access
window.loadDocuments = () => {
    if (window.app) {
        window.app.loadDocuments();
    }
};