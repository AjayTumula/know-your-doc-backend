import os
from datetime import timedelta

SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
FAISS_INDEX_PATH = "./faiss_index"
