from pydantic import BaseModel

class DocumentResponse(BaseModel):
    id: str
    name: str
    size: int
    type: str
    uploaded_at: str
    chunks_count: int
    status: str
