import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from app.config import FAISS_INDEX_PATH

embeddings_model = None
vector_store = None

def get_embeddings():
    global embeddings_model
    if embeddings_model is None:
        embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embeddings_model

def get_vector_store():
    global vector_store
    if vector_store is None and os.path.exists(FAISS_INDEX_PATH):
        vector_store = FAISS.load_local(FAISS_INDEX_PATH, get_embeddings(), allow_dangerous_deserialization=True)
    return vector_store

def save_vector_store(store):
    store.save_local(FAISS_INDEX_PATH)
