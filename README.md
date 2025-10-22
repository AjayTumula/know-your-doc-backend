

# ⚙️ Know Your Doc — Backend (FastAPI + FAISS)
This is the **FastAPI backend** for the **Know Your Doc** app — a document-based RAG system that uses **HuggingFace embeddings + FAISS vector search**.


## 🚀 Features
- 📥 Upload & process PDF/DOCX/TXT documents  
- 🧠 Embed chunks using `sentence-transformers/all-MiniLM-L6-v2`  
- 🔍 Vector search via FAISS  
- 💬 Query documents with natural-language chat  
- 🗂️ MongoDB stores metadata and chunks


## 🧩 Tech Stack
| Component | Technology |
|------------|-------------|
| Framework | FastAPI |
| Database | MongoDB Atlas |
| Vector DB | FAISS |
| Embeddings | HuggingFace Sentence Transformers |
| ORM | Motor (Async MongoDB client) |


## ⚙️ Setup Instructions

### 1️⃣ Navigate to backend folder
cd backend

### 2️⃣ Create and activate virtual environment
python -m venv .venv
source .venv/Scripts/activate     # Windows
# or
source .venv/bin/activate         # macOS / Linux


### 3️⃣ Install dependencies
pip install -r requirements.txt


### 4️⃣ Configure environment
MONGODB_URL=mongodb+srv://<your-atlas-uri>
FAISS_INDEX_PATH=./faiss_index
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

### ▶️ Run Backend Server
uvicorn app.main:app --reload




