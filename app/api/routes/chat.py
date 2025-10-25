import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from transformers import pipeline
from fastapi import APIRouter
from app.config import FAISS_INDEX_PATH, UPLOADS_PATH  # make sure UPLOADS_PATH points to your documents folder
from fastapi import HTTPException
from pydantic import BaseModel
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document

router = APIRouter()
# ------------------------------
# Load Embeddings
# ------------------------------
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ------------------------------
# Build FAISS index from documents
# ------------------------------
def build_faiss_index():
    all_docs = []

    for file_name in os.listdir(UPLOADS_PATH):
        if file_name.endswith(".txt"):
            loader = TextLoader(os.path.join(UPLOADS_PATH, file_name))
            docs = loader.load()

            # add 'source' metadata for each doc
            for doc in docs:
                doc.metadata["source"] = file_name
            all_docs.extend(docs)

    if not all_docs:
        raise ValueError("No documents found in uploads folder.")

    # split into chunks and preserve metadata
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = []
    for doc in all_docs:
        chunks = text_splitter.split_text(doc.page_content)
        for chunk in chunks:
            docs.append(Document(page_content=chunk, metadata=doc.metadata))

    embeddings = get_embeddings()
    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local(FAISS_INDEX_PATH)
    print("✅ FAISS index built successfully!")
    return vector_store


# ------------------------------
# Load FAISS vector store safely
# ------------------------------
def load_vector_store():
    embeddings = get_embeddings()
    if os.path.exists(FAISS_INDEX_PATH):
        try:
            return FAISS.load_local(
                FAISS_INDEX_PATH,
                embeddings,
                allow_dangerous_deserialization=True
            )
        except Exception:
            print("⚠️ FAISS index corrupted or incompatible. Rebuilding...")
            return build_faiss_index()
    else:
        print("⚠️ FAISS index missing. Building...")
        return build_faiss_index()

# ------------------------------
# Local LLM
# ------------------------------
def get_local_llm():
    generator = pipeline(
        "text2text-generation",
        model="google/flan-t5-base",
        max_length=512,
        temperature=0.3,
    )
    return HuggingFacePipeline(pipeline=generator)


# Request body model
class ChatRequest(BaseModel):
    question: str

# API route
@router.post("/ask")
async def ask_question(request: ChatRequest):
    try:
        result = await generate_answer(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------
# Main Chat Function
# ------------------------------
async def generate_answer(question: str):
    vector_store = load_vector_store()
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    llm = get_local_llm()

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
    )

    result = qa_chain({"query": question})
    answer = result["result"]

    sources = [
        {"document_name": doc.metadata.get("source", "Unknown"), "similarity_score": 1.0}
        for doc in result["source_documents"]
    ]
    return {"answer": answer, "sources": sources}
