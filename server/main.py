from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter,FieldCondition,MatchValue
from pathlib import Path
from datetime import datetime
from app.ingestion import ingest_document
from app.retriever import store_documents, get_retriver
from app.chain import get_qa_chain
from server.models import DocumentResponse, QuestionRequest, AnswerResponse, SourceDocument
from app.config import UPLOAD_DIR,QDRANT_PORT,QDRANT_HOST,QDRANT_COLLECTION_NAME
import os
import asyncio

app = FastAPI(
    title="DocuChat API",
    description="RAG based document Q&A system"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers = ["*"]
)

def save_file(path, data):
    with open(path, "wb") as f:
        f.write(data)

def delete_from_qdrant(file_path):
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    delete_filter = Filter(
        must=[
            FieldCondition(
                key="metadata.source",
                match=MatchValue(value=str(file_path))
            )
        ]
    )
    client.delete(
        collection_name=QDRANT_COLLECTION_NAME,
        points_selector=delete_filter
    )


Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# server check
@app.get("/health")
async def health_check():
    return{"status":"healthy","message":"DocuChat API is running"}

#upload PDF
@app.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    if file is None:
        raise HTTPException(400, "No file provided")
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are allowed")
    
    file_path = Path(UPLOAD_DIR) / file.filename

    contents = await file.read()
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, save_file, file_path, contents)

    chunks = await loop.run_in_executor(None, ingest_document, str(file_path))

    if not chunks:
        raise HTTPException(400, "Document has no extractable text. It may be scanned or corrupted")
    
    try:
        result = await loop.run_in_executor(None, store_documents, chunks, str(file_path))
    except Exception as e:
        #raise HTTPException(500, "Server not responding!!")
        print(f"UPLOAD ERROR: {str(e)}")
        raise HTTPException(500, f"Server not responding!! → {str(e)}")
        if result["status"] == "skipped":
            return result["message"]
    
    return {"message": result["message"], "filename": file.filename, "chunks": len(chunks)}

#asking question about PDF
@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(400, "Question cannot be empty")
    
    loop = asyncio.get_event_loop()

    chain = await loop.run_in_executor(None, get_qa_chain)

    response = await loop.run_in_executor(None, chain.invoke,{"input":question})

    result = response["answer"]

    documents = response["context"]

    source = []
    for doc in documents:
        source.append(SourceDocument(
            content = doc.page_content,
            page = doc.metadata.get("page"),
            source = doc.metadata.get("source")
        ))

    return AnswerResponse(
        answer=result,
        sources=source
    )

# getting all uploded pdf files
@app.get("/documents")
async def list_documents():
    try:
     files = [f for f in Path(UPLOAD_DIR).iterdir() if f.suffix == ".pdf"]
     documents = []
     for file in files:
         documents.append(
             {
                 "filename" : file.name,
                 "size_kb" : round(file.stat().st_size / 1024, 2),
                 "uploaded_at" : datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
             }
         )
     return {
         "documents": documents,
         "total" : len(documents)
     }
    except PermissionError:
        raise HTTPException(403, "cannot access uplodes folder")
    
    except Exception as e:
        raise HTTPException(500, f"Error listing documents: {str(e)}")
    

#delete any pdf file from uploads
@app.delete("/document/{filename}")
async def delete_documnet(filename: str):
    file_path = Path(UPLOAD_DIR) / filename

    if not file_path.exists():
        raise HTTPException(400, "Document not found!!")
    
    if file_path.suffix != ".pdf":
        raise HTTPException(400, "Only PDF files can be deleted")

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, os.remove, file_path) 
    
    try:
     await loop.run_in_executor(None, delete_from_qdrant, file_path)
    except:
        raise HTTPException(500, "File deleted but failed to remove vectors from Qdrant")
    
    return {
        "message": "Document deleted successfully",
        "filename": filename
    }