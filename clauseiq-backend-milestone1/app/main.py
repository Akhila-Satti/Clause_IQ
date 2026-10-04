from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.api.documents import router as documents_router
from app.routers.qa import router as qa_router
from app.routers.agreement_generator import (
    router as agreement_generator_router,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ClauseIQ Backend",
    description="Backend for the ClauseIQ agreement understanding desktop application.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "null",  # Electron file/webview origin during local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)
app.include_router(qa_router)
app.include_router(agreement_generator_router)


@app.get("/")
def root():
    return {"message": "ClauseIQ Backend is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
