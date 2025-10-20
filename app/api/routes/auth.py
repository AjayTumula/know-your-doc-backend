from fastapi import APIRouter, HTTPException, Depends
from app.schemas.user import UserLogin, UserCreate, Token
from app.services.auth_service import create_access_token

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    if user.email == "admin@company.com" and user.password == "password":
        token = create_access_token({"sub": user.email})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")
