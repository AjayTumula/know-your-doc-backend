import os
import io
import uuid
import PyPDF2
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.services.embedding_service import get_embeddings, get_vector_store, save_vector_store
from app.database import documents_collection, chunks_collection
from app.utils.text_processor import clean_text

# ------------------------------
# Document Processing Service
# ------------------------------

async def process_and_store_documents(files):
    """
    Main entry point — handles file upload, splitting, embedding, and saving.
    """
    embeddings = get_embeddings()
    vector_store = get_vector_store()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    uploaded_docs = []

    for file in files:
        content = await file.read()
        file_id = str(uuid.uuid4())
        file_name = file.filename
        file_type = file.content_type
        uploaded_at = datetime.utcnow().isoformat()

        # Step 1: Extract text
        text = extract_text_from_file(content, file_type)
        cleaned_text = clean_text(text)

        # Step 2: Split into chunks
        chunks = text_splitter.split_text(cleaned_text)

        # Step 3: Store document metadata
        doc_meta = {
            "_id": file_id,
            "name": file_name,
            "size": len(content),
            "type": file_type,
            "uploaded_at": uploaded_at,
            "chunks_count": len(chunks),
            "status": "processed"
        }
        await documents_collection.insert_one(doc_meta)

        # Step 4: Store chunks with embeddings
        for chunk in chunks:
            embedding = embeddings.embed_query(chunk)
            chunk_doc = {
                "doc_id": file_id,
                "text": chunk,
                "embedding": embedding
            }
            await chunks_collection.insert_one(chunk_doc)

        # Step 5: Update FAISS vector store
        if vector_store:
            vector_store.add_texts(chunks)
        else:
            from langchain_community.vectorstores import FAISS
            vector_store = FAISS.from_texts(chunks, embeddings)
        save_vector_store(vector_store)

        uploaded_docs.append({
            "id": file_id,
            "name": file_name,
            "size": len(content),
            "type": file_type,
            "uploaded_at": uploaded_at,
            "chunks_count": len(chunks),
            "status": "processed"
        })

    return uploaded_docs


def extract_text_from_file(content: bytes, file_type: str) -> str:
    """
    Extracts text content from PDF or plain text files.
    """
    if file_type == "application/pdf":
        return extract_text_from_pdf(content)
    elif file_type in ["text/plain", "application/octet-stream"]:
        return content.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def extract_text_from_pdf(content: bytes) -> str:
    """
    Extracts text from a PDF file using PyPDF2.
    """
    text = ""
    with io.BytesIO(content) as pdf_stream:
        reader = PyPDF2.PdfReader(pdf_stream)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text.strip()


async def delete_document(doc_id: str):
    """
    Deletes a document and its related chunks from the database.
    """
    await documents_collection.delete_one({"_id": doc_id})
    await chunks_collection.delete_many({"doc_id": doc_id})
    return {"message": f"Document {doc_id} deleted successfully"}
