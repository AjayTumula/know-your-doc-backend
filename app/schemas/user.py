from pydantic import BaseModel

class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    role: str = "employee"

class Token(BaseModel):
    access_token: str
    token_type: str
