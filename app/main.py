"""
FastAPI application entry point.
Run with:  uvicorn app.main:app --reload
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from app.routers.review import router as review_router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Code Review Agent starting up...")
    logger.info(f"  Foundry endpoint : {os.getenv('FOUNDRY_ENDPOINT', 'NOT SET')}")
    logger.info(f"  Tenant ID        : {os.getenv('TENANT_ID', 'NOT SET')}")
    yield
    logger.info("Code Review Agent shutting down.")


app = FastAPI(
    title="Code Review Agent",
    description=(
        "Multi-agent code review powered by Azure AI Foundry and LangGraph. "
        "Analyses code for security vulnerabilities, logic bugs, and quality issues."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the frontend origin during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(review_router, prefix="/api")

# Serve the frontend from /frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "code-review-agent"}
