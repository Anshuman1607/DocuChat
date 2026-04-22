from langchain_huggingface import HuggingFaceEmbeddings
from app.config import EMBEDDING_MODEL

def get_embedding_model() -> HuggingFaceEmbeddings:

    try:
     embedding_model = HuggingFaceEmbeddings(
         model_name = EMBEDDING_MODEL,
         model_kwargs = {'device' : 'cpu'},
         encode_kwargs = {"normalize_embeddings": True}
     )
     return embedding_model
    
    except Exception as e:
     raise ValueError(f"Failed to load embedding model: {str(e)}")