from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.document import DocumentResponse
from app.services.document_service import process_and_store_documents, delete_document
from typing import List

router = APIRouter()

@router.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(files: List[UploadFile] = File(...)):
    try:
        docs = await process_and_store_documents(files)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}")
async def remove_document(doc_id: str):
    return await delete_document(doc_id)
