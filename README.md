# ZEISS RAG Chatbot (Azure OpenAI + Azure AI Search)

A Retrieval-Augmented Generation (RAG) chatbot built with:

- Azure OpenAI (chat + embeddings)
- Azure AI Search (vector database)
- FastAPI (backend API)
- Docker (containerization)

## 🚀 Features

- PDF ingestion
- Text chunking with overlap
- Embedding generation (text-embedding-3-small)
- Vector search (Azure AI Search)
- Grounded responses with source citation
- REST API endpoints

## 🧱 Architecture

PDF → Chunking → Embeddings → Azure AI Search  
Query → Embed Query → Vector Retrieval → Chat Completion → Answer + Sources

## 🔌 API Endpoints

- `GET /health`
- `POST /upload`
- `POST /chat`

## 🐳 Run with Docker

```bash
docker build -t zeiss-rag-app .
docker run -p 8000:8000 --env-file .env zeiss-rag-app
