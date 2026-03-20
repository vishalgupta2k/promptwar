"""
LexSimple Backend — FastAPI Application
Main entry point for the LegalLens backend API.
"""

import sys
import os
import logging
from pathlib import Path

# Ensure project root is on the Python path so `agents` package is importable
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.analyze import router as analyze_router
from backend.routes.chat import router as chat_router
from backend.routes.draft import router as draft_router
from backend.routes.upload import router as upload_router

# ── App setup ─────────────────────────────────────────────────────────
app = FastAPI(
    title="LexSimple API",
    description="AI-powered legal document analysis — Google Gemini × LangGraph",
    version="1.0.0",
)

# ── CORS — allow Cloud Run frontend ───────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Security Headers Middleware ───────────────────────────────────────
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# ── Routes ────────────────────────────────────────────────────────────
app.include_router(upload_router, prefix="/api", tags=["upload"])
app.include_router(analyze_router, prefix="/api", tags=["analyze"])
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(draft_router, prefix="/api", tags=["draft"])


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "lexsimple-api"}
