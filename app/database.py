import motor.motor_asyncio
from app.config import MONGODB_URL

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.knowledge_base

users_collection = db.users
documents_collection = db.documents
chunks_collection = db.chunks
