import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from transformers import pipeline
from app.config import FAISS_INDEX_PATH


# ------------------------------
# Load Embeddings
# ------------------------------
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


# ------------------------------
# Load FAISS Vector Store
# ------------------------------
def load_vector_store():
    if not os.path.exists(FAISS_INDEX_PATH):
        raise FileNotFoundError("❌ FAISS index not found. Upload documents first.")
    embeddings = get_embeddings()
    return FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)


# ------------------------------
# Local LLM (for generation)
# ------------------------------
def get_local_llm():
    """
    A small, local Hugging Face model used for question-answering.
    You can replace this with any other model that runs locally.
    """
    generator = pipeline(
        "text2text-generation",
        model="google/flan-t5-base",  # good small model for QA
        max_length=512,
        temperature=0.3,
    )
    return HuggingFacePipeline(pipeline=generator)


# ------------------------------
# Main Chat Function
# ------------------------------
async def generate_answer(question: str):
    try:
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

        sources = []
        for doc in result["source_documents"]:
            sources.append({
                "document_name": doc.metadata.get("source", "Unknown"),
                "similarity_score": 1.0,
            })

        return {"answer": answer, "sources": sources}

    except FileNotFoundError as e:
        return {"error": str(e)}
    except Exception as e:
        print("🔥 ERROR in generate_answer:", e)
        raise e
