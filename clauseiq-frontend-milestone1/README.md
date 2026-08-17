# ClauseIQ — Frontend Milestone 1

React + TypeScript + Electron foundation for the ClauseIQ desktop application.

## Included
- Electron desktop shell
- React/TypeScript UI
- Dashboard
- PDF/DOCX/TXT upload UI
- FastAPI upload integration with demo fallback
- Agreement analysis dashboard
- Attention/risk cards
- Clause list and original-clause/explanation viewer
- Sidebar navigation
- Responsive layout
- Electron Ctrl/Cmd+Shift+A show/hide shortcut

## Run

```bash
npm install
npm run desktop
```

The upload API is expected at `http://127.0.0.1:8000/documents/upload`.
If the backend is unavailable, the UI falls back to demo data so frontend development can continue.

## Milestone 1 boundary
Ask Agreement, personalization, RAG, risk engine implementation, and Clause Assistant are intentionally placeholders. They belong to later milestones according to the project plan.
