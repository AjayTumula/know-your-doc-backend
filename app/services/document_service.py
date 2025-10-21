import os
import io
import uuid
import PyPDF2
from datetime import datetime
from docx import Document as DocxDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi import HTTPException

from app.services.embedding_service import (
    get_embeddings,
    get_vector_store,
    save_vector_store,
)
from app.database import documents_collection, chunks_collection
from app.utils.text_processor import clean_text


# ------------------------------
# Document Processing Service
# ------------------------------

async def process_and_store_documents(files):
    """
    Handles file upload, text extraction, splitting, embedding, and saving.
    """
    try:
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

            # --- Step 1: Extract text ---
            try:
                text = extract_text_from_file(content, file_type)
                cleaned_text = clean_text(text)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to read {file_name}: {str(e)}")

            if not cleaned_text.strip():
                raise HTTPException(status_code=400, detail=f"No readable text in {file_name}")

            # --- Step 2: Split into chunks ---
            chunks = text_splitter.split_text(cleaned_text)

            # --- Step 3: Store document metadata ---
            doc_meta = {
                "_id": file_id,
                "name": file_name,
                "size": len(content),
                "type": file_type,
                "uploaded_at": uploaded_at,
                "chunks_count": len(chunks),
                "status": "processed",
            }
            await documents_collection.insert_one(doc_meta)

            # --- Step 4: Store chunks with embeddings ---
            for chunk in chunks:
                embedding = embeddings.embed_query(chunk)
                chunk_doc = {"doc_id": file_id, "text": chunk, "embedding": embedding}
                await chunks_collection.insert_one(chunk_doc)

            # --- Step 5: Update FAISS vector store ---
            if vector_store:
                vector_store.add_texts(chunks)
            else:
                from langchain_community.vectorstores import FAISS
                vector_store = FAISS.from_texts(chunks, embeddings)
            save_vector_store(vector_store)

            # --- Step 6: Build response ---
            uploaded_docs.append(
                {
                    "id": file_id,
                    "name": file_name,
                    "size": len(content),
                    "type": file_type,
                    "uploaded_at": uploaded_at,
                    "chunks_count": len(chunks),
                    "status": "processed",
                }
            )

        return uploaded_docs

    except Exception as e:
        print(f"🔥 ERROR in document processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------
# Text Extraction Helpers
# ------------------------------

def extract_text_from_file(content: bytes, file_type: str) -> str:
    """
    Extracts text content from PDF, DOCX, or plain text files.
    """
    # --- PDF ---
    if file_type == "application/pdf":
        return extract_text_from_pdf(content)

    # --- DOCX / DOC ---
    elif file_type in [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ]:
        return extract_text_from_docx(content)

    # --- TXT ---
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


def extract_text_from_docx(content: bytes) -> str:
    """
    Extracts text from a DOCX file using python-docx.
    """
    doc = DocxDocument(io.BytesIO(content))
    return "\n".join([para.text for para in doc.paragraphs]).strip()


# ------------------------------
# Deletion Logic
# ------------------------------

async def delete_document(doc_id: str):
    """
    Deletes a document and its related chunks from MongoDB.
    """
    await documents_collection.delete_one({"_id": doc_id})
    await chunks_collection.delete_many({"doc_id": doc_id})
    return {"message": f"Document {doc_id} deleted successfully"}


async def get_all_documents():
    """
    Fetch all document metadata from MongoDB.
    """
    docs_cursor = documents_collection.find()
    docs = await docs_cursor.to_list(length=None)

    return [
        {
            "id": doc["_id"],
            "name": doc["name"],
            "size": doc["size"],
            "type": doc["type"],
            "uploaded_at": doc["uploaded_at"],
            "chunks_count": doc.get("chunks_count", 0),
            "status": doc.get("status", "unknown"),
        }
        for doc in docs
    ]

