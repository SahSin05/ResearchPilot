ResearchPilot AI — Day 2 Research Data Foundation
A full-stack AI research assistant with academic paper discovery, document ingestion, persistent research storage, and RAG-ready document chunking.
Stack
- Frontend: React + Vite + JavaScript
- Backend: FastAPI + Python
- Database: SQLite + SQLAlchemy
- Academic literature: OpenAlex API
- Document extraction: PyMuPDF + python-docx
- Local orchestration: Docker Compose
Requirements
- Node.js 20+ (or a current LTS release)
- Python 3.11+
- Docker Desktop (optional, for Compose)
- OpenAlex API key
Run locally
1. Backend
From the repository root:
cd backend

Create and activate the virtual environment:
python -m venv .venv

Windows PowerShell:
.venv\Scripts\Activate.ps1

macOS/Linux:
source .venv/bin/activate

Install dependencies:
pip install -r requirements.txt

Start the backend:
python -m uvicorn app.main:app --reload --app-dir backend

API docs:
http://localhost:8000/docs
Health check:
http://localhost:8000/health
2. Frontend
Open another terminal:
cd frontend
npm install
npm run dev

Open the URL Vite prints, usually:
http://localhost:5173
The frontend connects to the backend at:
http://localhost:8000

Environment variables
Create a .env file in the repository root:
OPENALEX_API_KEY=your_openalex_api_key

Do not commit .env to Git.
Day 2 features
Academic paper discovery
- OpenAlex integration
- Paper search
- Author filtering
- Publication-year filtering
- Pagination
- Paper normalization
- Paper persistence in SQLite
- Paper detail retrieval
Document ingestion
- PDF upload
- DOCX upload
- TXT upload
- File validation
- Original file storage
- Text extraction
- Document metadata persistence
Research library
- Persistent document library
- Document listing
- Frontend upload interface
- Backend/frontend integration
RAG preparation
- Text chunking
- Chunk overlap
- Persistent document chunks
- Chunk metadata including:
  - Document ID
  - Chunk index
  - Chunk text
  - Character count
Database structure
Day 2 introduces persistent research storage:
SQLite
│
├── papers
│   ├── OpenAlex ID
│   ├── title
│   ├── publication year
│   ├── DOI
│   ├── authors
│   └── abstract
│
├── documents
│   ├── filename
│   ├── file type
│   ├── file size
│   ├── page count
│   ├── extracted text
│   ├── file path
│   ├── processing status
│   └── user ID
│
└── document_chunks
    ├── document ID
    ├── chunk index
    ├── chunk text
    └── character count

Day 2 acceptance checks
- [x] FastAPI /health returns {"status":"ok"}
- [x] React frontend loads
- [x] UI reports backend connectivity
- [x] OpenAlex paper search works
- [x] OpenAlex API key configured
- [x] Papers can be persisted in SQLite
- [x] PDF extraction works
- [x] DOCX extraction works
- [x] TXT extraction works
- [x] Documents can be uploaded
- [x] Uploaded files are stored locally
- [x] Documents appear in My Library
- [x] Documents persist after frontend reload
- [x] Document chunks are generated
- [x] Document chunks are persisted in SQLite
- [x] Day 2 changes committed to Git
- [x] Day 2 changes pushed to GitHub
Day 2 project structure
ResearchPilot/
├── backend/
│   ├── app/
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   └── models.py
│   │   ├── routes/
│   │   │   ├── documents.py
│   │   │   └── papers.py
│   │   ├── schemas/
│   │   │   ├── document.py
│   │   │   └── paper.py
│   │   ├── services/
│   │   │   ├── chunking.py
│   │   │   ├── documents.py
│   │   │   └── openalex.py
│   │   └── main.py
│   ├── test_chunking.py
│   ├── test_openalex.py
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       └── App.jsx
│
├── researchpilot.db
└── README.md

Git checkpoint
Day 2 commit:
6290a17 — Complete Day 2 research data foundation

Notes
Day 2 establishes the persistent research-data foundation for ResearchPilot AI.
The next phase will build the RAG layer:
Document chunks
      ↓
Embeddings
      ↓
Vector store
      ↓
Semantic retrieval
      ↓
LLM
      ↓
Grounded answers
      ↓
Citations
