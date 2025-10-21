import os
from fastapi import UploadFile

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_uploaded_file(file: UploadFile) -> str:
    """
    Saves an uploaded file to the uploads directory and returns its file path.
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return file_path


def delete_file(path: str):
    """
    Deletes a file if it exists.
    """
    if os.path.exists(path):
        os.remove(path)
