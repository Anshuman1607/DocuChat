from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import CHUNK_SIZE, CHUNK_OVERLAP
import os

def ingest_document(file_path: str) -> list:
    try:
     if not os.path.exists(file_path):
        raise ValueError("File does not exist at the provided path.")
     
     loader = PyPDFLoader(file_path)
     docs = loader.load()

    except Exception as e:
        raise ValueError(f"Error occurred while loading the document: {e}")

    if not docs:
        raise ValueError("No documents found in the provided file.")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(docs)

    return chunks