import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY', None)

EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', "all-MiniLM-L6-v2")

QDRANT_URL = os.getenv('QDRANT_URL', None)
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY', None)
QDRANT_COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME', "docuchat")

CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))

UPLOAD_DIR = os.getenv('UPLOAD_DIR', "uploads")

LLM_MODEL_NAME = os.getenv('LLM_MODEL_NAME', "llama-3.1-8b-instant")

