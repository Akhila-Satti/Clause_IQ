# ClauseIQ Backend — Milestone 1

Python + FastAPI backend for the ClauseIQ Electron/React frontend.

## What this backend currently does

PDF/DOCX/TXT
→ FastAPI upload
→ text extraction
→ rule-based clause segmentation
→ basic category/risk signals
→ PostgreSQL storage
→ analysis API

It matches the frontend's current API contract:

- `POST /documents/upload`
- `GET /documents`
- `GET /documents/{id}`
- `GET /documents/{id}/clauses`
- `GET /documents/{id}/analysis`

The frontend in the supplied project currently uses demo analysis data after upload. Once you are ready, change the frontend to call `getAnalysis(documentId)` and render the returned analysis.

## 1. Start PostgreSQL

Docker is the easiest option:

```bash
docker compose up -d
```

## 2. Create Python environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment

Copy `.env.example` to `.env`.

The default database URL expects the included Docker PostgreSQL container.

## 5. Start API

```bash
uvicorn app.main:app --reload
```

API:
`http://127.0.0.1:8000`

Swagger:
`http://127.0.0.1:8000/docs`

## Important scope note

The current risk/category logic is a transparent Milestone-1 baseline. It is NOT a legal validity determination and is not the final risk engine.

Gemini, embeddings, pgvector/RAG, user preferences, scenario analysis, authentication, and clause drafting should be added in later milestones.
