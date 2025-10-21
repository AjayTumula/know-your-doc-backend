# app/api/routes/documents.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import traceback

from app.schemas.document import DocumentResponse
from app.services.document_service import (
    process_and_store_documents,
    delete_document,
    get_all_documents,
)
from app.database import documents_collection  # ✅ Import your MongoDB collection

router = APIRouter()

# -------------------------
# 📤 Upload Documents
# -------------------------
@router.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(files: List[UploadFile] = File(...)):
    try:
        docs = await process_and_store_documents(files)
        return docs
    except Exception as e:
        print("\n🔥 ERROR in /documents/upload:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# 📄 Get All Documents
# -------------------------
@router.get("/", response_model=List[DocumentResponse])
async def get_documents():
    try:
        docs = await documents_collection.find().to_list(None)
        for doc in docs:
            doc["id"] = str(doc.pop("_id", ""))
        return docs
    except Exception as e:
        print("\n🔥 ERROR in /documents:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# ❌ Delete Document
# -------------------------
@router.delete("/{doc_id}")
async def remove_document(doc_id: str):
    """
    Delete a document and its associated chunks from MongoDB.
    """
    try:
        return await delete_document(doc_id)
    except Exception as e:
        print("\n🔥 ERROR in /documents/delete:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
