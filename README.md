# ResearchPilot AI — Day 1 Starter

A full-stack starter for an AI research paper assistant.

## Stack
- Frontend: React + Vite + JavaScript
- Backend: FastAPI + Python
- Local orchestration: Docker Compose

## Requirements
- Node.js 20+ (or a current LTS release)
- Python 3.11+
- Docker Desktop (optional, for Compose)

## Run locally

### 1. Backend
```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

### 2. Frontend
Open another terminal:
```bash
cd frontend
npm install
npm run dev
```
Open the URL Vite prints (usually http://localhost:5173).

The frontend calls the backend at `VITE_API_BASE_URL`, defaulting to `http://localhost:8000`.

## Run with Docker Compose
From the repository root:
```bash
docker compose up --build
```
- Frontend: http://localhost:5173
- Backend docs: http://localhost:8000/docs

## Day 1 acceptance checks
- [ ] FastAPI `/health` returns `{"status":"ok"}`
- [ ] React page loads
- [ ] UI reports backend connectivity
- [ ] No secrets are committed
- [ ] Git repository has an initial commit

## Notes
- This is a starter scaffold, not the complete product.
- Search, uploads, RAG, evaluation, authentication, and AWS deployment are added in later milestones.
- Do not place LLM provider keys or AWS secrets in frontend variables. Anything prefixed with `VITE_` is exposed to the browser.
