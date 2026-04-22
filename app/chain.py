from langchain_groq import ChatGroq
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from app.retriever import get_retriver
from app.config import GROQ_API_KEY,LLM_MODEL_NAME
from app.prompts import QA_PROMPT

def get_llm():
    if GROQ_API_KEY is None:
        raise ValueError("GROQ_API_KEY is not set.")
    
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name = LLM_MODEL_NAME,
        temperature=0
    )

    return llm

def get_qa_chain():
    llm = get_llm()
    retriever = get_retriver()
    
    chain = create_stuff_documents_chain(llm=llm, prompt=QA_PROMPT)

    retrieval_chain = create_retrieval_chain(retriever, chain)

    return retrieval_chain