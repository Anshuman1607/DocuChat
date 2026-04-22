# ◈ DocuChat

A RAG-based document Q&A system. Upload PDF files and ask questions — answers are grounded in your documents with source citations.

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq — `llama-3.1-8b-instant` |
| Embeddings | HuggingFace — `all-MiniLM-L6-v2` |
| Vector Database | Qdrant (Docker) |
| Backend | FastAPI |
| RAG Framework | LangChain |
| Frontend | HTML / CSS / JS |

---

## Architecture

```
User uploads PDF
      ↓
PyPDFLoader → reads pages
      ↓
RecursiveCharacterTextSplitter → chunks
      ↓
HuggingFace Embeddings → vectors
      ↓
Qdrant → stores vectors + metadata
      ↓
User asks question
      ↓
Query embedded → similarity search → top 4 chunks
      ↓
Groq LLM + context → answer + sources
```

---

## Project Structure

```
docuchat/
├── app/
│   ├── config.py          # environment variables & settings
│   ├── ingestion.py       # PDF loading & chunking
│   ├── embeddings.py      # HuggingFace embedding model
│   ├── retriever.py       # Qdrant vector store operations
│   ├── chain.py           # LLM + RAG chain
│   └── prompts.py         # system prompt template
├── server/
│   ├── main.py            # FastAPI app & endpoints
│   └── models.py          # Pydantic request/response models
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── uploads/               # uploaded PDFs stored here
├── .env                   # API keys (not committed)
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- Docker (for Qdrant)
- Groq API key — [console.groq.com](https://console.groq.com)

### 1. Clone the repository

```bash
git clone https://github.com/Anshuman1607/docuchat.git
cd docuchat
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root:

```env
GROQ_API_KEY=your_groq_api_key_here
EMBEDDING_MODEL=all-MiniLM-L6-v2
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=docuchat
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
UPLOAD_DIR=uploads
LLM_MODEL_NAME=llama-3.1-8b-instant
```

### 5. Start Qdrant with Docker

```bash
docker run -p 6333:6333 -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

### 6. Start the FastAPI server

```bash
uvicorn server.main:app --reload
```

Server runs at `http://localhost:8000`

### 7. Open the frontend

Open `frontend/index.html` in your browser directly, or use Live Server in VS Code.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Check API and Qdrant status |
| `POST` | `/upload` | Upload and index a PDF |
| `POST` | `/ask` | Ask a question about uploaded docs |
| `GET` | `/documents` | List all uploaded documents |
| `DELETE` | `/document/{filename}` | Delete a document |

### Example: Upload a PDF

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@yourfile.pdf"
```

Response:
```json
{
  "message": "Document uploaded successfully",
  "filename": "yourfile.pdf",
  "chunks": 42
}
```

### Example: Ask a question

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?"}'
```

Response:
```json
{
  "answer": "The main topic is...",
  "sources": [
    {
      "content": "relevant chunk text...",
      "page": 3,
      "source": "uploads/yourfile.pdf"
    }
  ]
}
```

---

## How RAG Works

RAG (Retrieval-Augmented Generation) has two phases:

**Indexing** — when you upload a PDF:
1. PDF is split into overlapping text chunks
2. Each chunk is converted into a vector (embedding)
3. Vectors are stored in Qdrant with metadata (page, source)

**Retrieval** — when you ask a question:
1. Question is converted into a vector
2. Qdrant finds the top 4 most similar chunks
3. Chunks are injected into the LLM prompt as context
4. LLM generates an answer grounded in that context

This prevents hallucination — the LLM can only answer using what's in your documents.

---

## Features

- Upload PDF documents via drag & drop
- Ask natural language questions
- Answers grounded in document context only
- Source citations with page numbers
- Duplicate document detection
- Delete documents from store
- Live API health indicator
- Clean dark-themed UI

---

## Future Improvements

- Support for `.txt` and `.docx` files
- Streaming responses (token by token)
- User authentication
- Deploy on Railway / Render
- Multi-user support
- Conversation memory across turns

---

## License

MIT
