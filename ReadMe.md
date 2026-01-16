# Code Budy 🤖📂

code budy  is an AI-powered codebase assistant that allows users to:

- Authenticate and manage multiple projects
- Index a local repository into a vector database (ChromaDB)
- Ask questions about the codebase
- Request safe, controlled code modifications
- Review, apply, or reject AI-proposed changes
- Persist full chat history, actions, and diffs per project

The system is designed with **strict safety rules** so the AI:
- Can only modify existing files
- Can only change one file at a time
- Never applies changes automatically without user approval

---

## 🧠 Architecture Overview

### Backend (FastAPI + MongoDB + ChromaDB)
- **FastAPI** – REST API
- **MongoDB** – Users, projects, chat history, diffs
- **ChromaDB** – Vector search over indexed source code
- **JWT Auth** – Secure user authentication
- **LLM integration** – Code-aware AI assistant
- **Background indexing** – Non-blocking repo indexing

### Frontend (Vite + React + TypeScript)
- Project dashboard
- Chat interface
- Apply / Reject AI changes
- View full chat & diff history
- Authenticated API access

---


---

## ⚙️ Prerequisites

- Python **3.9+**
- Node.js **18+**
- MongoDB (local or Atlas)
- Git

---

## 🚀 Backend Setup

### 1️⃣ Create Python Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # macOS / Linux
# or
venv\Scripts\activate      # Windows


2️⃣ Install Backend Dependencies
pip install -r requirements.txt

3️⃣ Create .env File

Inside the backend/ directory, create a file named .env:

# Server
PORT=8000

# MongoDB
MONGO_URI=mongodb://127.0.0.1:27017/repo_agent

# JWT
JWT_SECRET=super_secret_repo_agent_key
JWT_EXPIRES_IN=7d

# LLM (example – adjust to your provider)
GEMINI_API_KEY=YOUR_API_KEY_HERE


⚠️ Never commit .env to GitHub.

4️⃣ Start Backend Server
uvicorn app.main:app --reload


Backend will run at:

http://127.0.0.1:8000


Swagger docs available at:

http://127.0.0.1:8000/docs

🌐 Frontend Setup
1️⃣ Install Frontend Dependencies
cd frontend
npm install

2️⃣ Start Frontend Dev Server
npm run dev

